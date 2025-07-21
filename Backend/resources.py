import builtins
from collections import OrderedDict
import csv
from datetime import date, timedelta, datetime
from zoneinfo import ZoneInfo
import pytz
from functools import wraps
import io
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import pandas as pd
from flask import request, jsonify
from flask_restx import Resource, Namespace, reqparse, marshal, fields
from flask_jwt_extended import create_access_token, current_user, get_jwt_identity, jwt_required, get_jwt, verify_jwt_in_request, JWTManager
from sqlalchemy import distinct, exists, func, null,extract
from sqlalchemy.orm import aliased, joinedload, subqueryload, contains_eager
import logging

from Backend.models import *
# from .api_models import *
# from .helper import *

from werkzeug.datastructures import FileStorage
from werkzeug.exceptions import Unauthorized

logger = logging.getLogger(__name__)

authorizations = {
    "jsonwebtoken": {
        "type": "apiKey",
        "in": "header",
        "name": "Authorization"
    }
}

sc = Namespace("sc", description="SilverCare Backend API Namespace", authorizations=authorizations)

user_update_model = sc.model('UserUpdate', {
    'first_name': fields.String(required=False),
    'last_name': fields.String(required=False),
    'username': fields.String(required=False),
    'role': fields.String(required=False),
    'profile_picture': fields.String(required=False),
})

create_medicine_model = sc.model('CreateMedicine', {
    'title': fields.String(required=True),
    'description': fields.String(required=True),
    'image': fields.String(required=True),
})

assign_medicine_model = sc.model('AssignMedicine', {
    'medicine_id': fields.Integer(required=True),
    'senior_citizen_id': fields.Integer(required=False),
    'dosage': fields.Integer(required=True),
    'start_date': fields.String(required=True, description='YYYY-MM-DD'),
    'end_date': fields.String(required=True, description='YYYY-MM-DD'),
    'breakfast_before': fields.Boolean(required=False, default=False),
    'breakfast_after': fields.Boolean(required=False, default=False),
    'lunch_before': fields.Boolean(required=False, default=False),
    'lunch_after': fields.Boolean(required=False, default=False),
    'dinner_before': fields.Boolean(required=False, default=False),
    'dinner_after': fields.Boolean(required=False, default=False),
})

unassign_medicine_model = sc.model('UnassignMedicine', {
    'user_id': fields.Integer(required=False, description='Senior Citizen ID'),
    'medicine_id': fields.Integer(required=True, description='ID of medicine to be removed'),
})

report_model = sc.model("StatusReportInput", {
    "user_id": fields.Integer(required=False, description="Senior Citizen ID"),

    "month": fields.Integer(required=True, description="Month (1-12)"),
    "year": fields.Integer(required=True, description="Year (e.g., 2025)")
})

medicine_reminder_model = sc.model("MedicineReminder", {
    "reminder_id": fields.Integer(required=True),
    "user_med_map_id": fields.Integer(required=True),
    "reminder_time": fields.String(required=True, example="breakfast_before"),
    "notification_type": fields.String(required=True, example="push"),
    "message": fields.String(required=True),
    "active": fields.Boolean(default=True),
})

list_medicine_reminder_model = sc.model("ListMedicineReminder", {
    "user_med_map_id": fields.Integer(required=True)
})

send_reminder_model = sc.model('SendReminderModel', {
    'user_id': fields.Integer(required=True, description='ID of the user to send reminder to'),
    'medicine_id': fields.Integer(required=True, description='ID of the medicine to send reminder for')
})

mark_medicine_taken_model = sc.model("MarkMedicineTaken", {
    'medicine_id': fields.Integer(required=True),
    'slot': fields.String(required=True, example="breakfast_before"),
})

health_entry_model = sc.model("HealthEntry", {
    'bp_systolic': fields.Integer(required=True),
    'bp_diastolic': fields.Integer(required=True),
    'sugar_level': fields.Float(required=True),
})

# To verify token
@sc.route("/api/verify-token")
class VerifyToken(Resource):
    
    def get(self):
        "Verify JWT token"
        try:
            # Verify the JWT in the request
            verify_jwt_in_request()  # Raises an exception if the token is invalid
            claims = get_jwt()  # Extract claims from the token
            return {
                "valid": True,
                "claims": claims,
                "message": "Token is valid",
                "role": claims.get('role')

            }, 200
        except Unauthorized as e:
            return {
                "valid": False,
                "message": "Invalid or expired token"
            }, 401
        except Exception as e:
            return {
                "valid": False,
                "message": "An error occurred during token verification"
            }, 500
        
# Edit user
@sc.route('/user/<int:user_id>')
class EditUser(Resource):
    @jwt_required()
    @sc.expect(user_update_model, validate=True)
    def put(self, user_id):
        """Update user details"""
        data = request.get_json()
        user_id = current_user.id # Only concerned user can only change it's own details
        user = User.query.get(user_id)

        if not user:
            return {'message': 'User not found'}, 404        
        # to check validity of user
        if (user_id != user):
            return {'message': 'You are not authorized to update other user details'}, 403

        # Update fields only if present in data
        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        user.username = data.get('username', user.username)
        user.role = data.get('role', user.role)
        user.profile_picture = data.get('profile_picture', user.profile_picture)

        # Handling password update (only if provided and not empty)
        if 'password' in data and data['password']:
            user.set_password(data['password'])

        try:
            db.session.commit()
            return {'message': 'User updated successfully'}, 200
        except Exception as e:
            db.session.rollback()
            return {'message': 'Failed to update user', 'error': str(e)}, 500

# <------------------------------------CRUD operations for Medicine------------------------------------>


#Create medicine
@sc.route('/create-medicine')
class CreateMedicine(Resource):
    @jwt_required()
    @sc.expect(create_medicine_model, validate=True)
    def post(self):
        """Create new medicine entry"""
        data = request.get_json()
        user_id = get_jwt_identity()

        medicine = Medicine(
            title=data['title'],
            description=data['description'],
            user_id=user_id,
            image=data.get('image')
        )

        try:
            db.session.add(medicine)
            db.session.commit()
            return {'message': 'Medicine created successfully', 'medicine_id': medicine.id}, 201
        except Exception as e:
            db.session.rollback()
            return {'message': 'Failed to create medicine', 'error': str(e)}, 500
        
#Get all medicines
@sc.route('/all-medicines')
class AllMedicineNames(Resource):
    def get(self):
        """Get all medicine names"""
        medicines = Medicine.query.filter_by(status="approved").all()

        result = [
            {
                "title": med.title,
                "description": med.description,
                "image": med.image
            }
            for med in medicines
        ]
        return {"medicines": result}, 200

#Edit medicine
@sc.route('/edit-medicine/<int:medicine_id>')
class EditMedicine(Resource):
    @jwt_required()
    @sc.expect(create_medicine_model, validate=True)
    def put(self, medicine_id):
        """Update a medicine entry by ID."""
        user_id = get_jwt_identity()
        user_role = current_user.role

        if user_role != "admin":
            return {'message': 'Unauthorized'}, 403
        # Check if the medicine exists and belongs to the user
        medicine = Medicine.query.filter_by(id=medicine_id).first()


        if not medicine:
            return {'message': 'Medicine not found or unauthorized'}, 404

        data = request.get_json()
        medicine.title = data.get('title', medicine.title)
        medicine.description = data.get('description', medicine.description)
        medicine.image = data.get('image', medicine.image)

        try:
            db.session.commit()
            return {'message': 'Medicine updated successfully'}, 200
        except Exception as e:
            db.session.rollback()
            return {'message': 'Failed to update medicine', 'error': str(e)}, 500

#Delete medicine
@sc.route('/delete-medicine/<int:medicine_id>')
class DeleteMedicine(Resource):
    @jwt_required()
    def delete(self, medicine_id):
        """Delete a medicine entry by ID."""
        user_id = get_jwt_identity()
        user_role = current_user.role

        if user_role != "admin":
            return {'message': 'Unauthorized'}, 403
        
        medicine = Medicine.query.filter_by(id=medicine_id).first()

        if not medicine:
            return {'message': 'Medicine not found or unauthorized'}, 404

        try:
            db.session.delete(medicine)
            db.session.commit()
            return {'message': 'Medicine deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            return {'message': 'Failed to delete medicine', 'error': str(e)}, 500

#<---------------------------------------------------------------------------------------------------------------->


# <------------------------------------CRUD operations to assign-medicine------------------------------------>

# To assign medicine to senior citizen
@sc.route("/assign-medicine", methods=["POST"])
class AssignMedicine(Resource):
    @jwt_required()
    @sc.expect(assign_medicine_model, validate=True)
    def post(self):
        """Assign a medicine to a senior citizen."""
        data = request.get_json()
        user_role = current_user.role

        if(user_role == "senior_citizen"):
            user_id = current_user.id
        elif user_role == "care_giver":
            user_id = data.get("senior_citizen_id")
            if not user_id:
                return {"error": "Missing 'senior_citizen_id' for caregiver"}, 400

            # Check caregiver-senior relationship
            is_approved = CaregiverSeniorMap.query.filter_by(
                caregiver_id=current_user.id,
                senior_id=user_id,
                status='approved'
            ).first()

            if not is_approved:
                return {"error": "You are not an approved caregiver for this senior citizen."}, 403
        
        try:
            assignment = UserMedMap(
                user_id=user_id,
                medicine_id=data["medicine_id"],
                dosage=data["dosage"],
                start_date=datetime.strptime(data["start_date"], "%Y-%m-%d"),
                end_date=datetime.strptime(data["end_date"], "%Y-%m-%d"),
                breakfast_before=data.get("breakfast_before", False),
                breakfast_after=data.get("breakfast_after", False),
                lunch_before=data.get("lunch_before", False),
                lunch_after=data.get("lunch_after", False),
                dinner_before=data.get("dinner_before", False),
                dinner_after=data.get("dinner_after", False),
            )
            db.session.add(assignment)
            db.session.flush() 
            start_date = assignment.start_date.date()
            end_date = assignment.end_date.date()
            delta = (end_date - start_date).days + 1
            for i in range(delta):
                current_date = start_date + timedelta(days=i)
                status = Status(
                    user_med_map_id=assignment.id,
                    date=current_date,
                    breakfast_before=False if assignment.breakfast_before else None,
                    breakfast_after=False if assignment.breakfast_after else None,
                    lunch_before=False if assignment.lunch_before else None,
                    lunch_after=False if assignment.lunch_after else None,
                    dinner_before=False if assignment.dinner_before else None,
                    dinner_after=False if assignment.dinner_after else None
                )
                db.session.add(status)
            db.session.commit()
            return {"message": "Medicine assigned and status tracking initialized."}, 201
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

# To unassign medicine for senior citizen
@sc.route("/unassign-medicine",methods=["DELETE"])
class UnassignMedicine(Resource):
    @jwt_required()
    @sc.expect(unassign_medicine_model, validate=True)
    def delete(self):
        """Unassign a medicine from a senior citizen."""
        data = request.get_json()
        user_role = current_user.role

        if(user_role == "senior_citizen"):
            user_id = current_user.id
        elif user_role == "care_giver":
            user_id = data.get("senior_citizen_id")
            if not user_id:
                return {"error": "Missing 'senior_citizen_id' for caregiver"}, 400

            # Check caregiver-senior relationship
            is_approved = CaregiverSeniorMap.query.filter_by(
                caregiver_id=current_user.id,
                senior_id=user_id,
                status='approved'
            ).first()

            if not is_approved:
                return {"error": "You are not an approved caregiver for this senior citizen."}, 403


        medicine_id = data['medicine_id']

        assignment=UserMedMap.query.filter_by(user_id=user_id, medicine_id=medicine_id).first()
        if not assignment:
                return {"error": "Assignment not found."}, 404
        try:
            db.session.delete(assignment)
            db.session.commit()
            return {"message": "Medicine unassigned successfully."}, 200
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500
        

# To get all the medicine assigned to a senior citizen
@sc.route('/my-medicines')
class MyMedicines(Resource):
    @jwt_required()
    def get(self):
        try:
            user_id = get_jwt_identity()

            # Simulate current_user loading
            current_user = User.query.get(user_id)
            if not current_user:
                return {
                    "error": "User not found.",
                    "code": "USER_NOT_FOUND"
                }, 404

            user_role = current_user.role

            if user_role != "senior_citizen":
                return {
                    "error": "You are not authorized to access this resource.",
                    "code": "FORBIDDEN_ROLE"
                }, 403

            user_meds = UserMedMap.query.filter_by(user_id=user_id).all()
            if not user_meds:
                return {
                    "error": "No medicines found for this user.",
                    "code": "NO_MEDICINES"
                }, 404

            result = []
            for um in user_meds:
                med = um.medicine

                if not med:
                    continue  # Skip this entry if medicine relationship is broken

                result.append({
                    "medicine_id": med.id,
                    "title": med.title,
                    "description": med.description,
                    "dosage": um.dosage,
                    "start_date": um.start_date.isoformat() if um.start_date else None,
                    "end_date": um.end_date.isoformat() if um.end_date else None,
                    "image": med.image,
                    "is_approved": med.is_approved
                })

            return {
                "medicines": result
            }, 200

        except SQLAlchemyError as e:
            return {
                "error": "Database error occurred.",
                "details": str(e),
                "code": "DB_ERROR"
            }, 500

        except Exception as e:
            return {
                "error": "An unexpected error occurred.",
                "details": str(e),
                "code": "INTERNAL_SERVER_ERROR"
            }, 500

# <---------------------------------------------------------------------------------------------------------------->

# <------------------------------------Getting Status of medicine------------------------------------>

# getting medicine status
@sc.route("/medicine-status/<int:medicine_id>", methods=["GET"])
class MedicineStatus(Resource):
    @jwt_required()
    @sc.doc(params={
        'date': 'Date in YYYY-MM-DD format (as query parameter)'
    })
    def get(self, medicine_id):
        """Get the status of a specific medicine for a senior citizen."""
        try:
            user_id = get_jwt_identity()
            date_str = request.args.get('date')
            
            if not date_str:
                return {
                    "error": "Date is required in 'YYYY-MM-DD' format as a query parameter.",
                    "code": "DATE_MISSING"
                }, 400
            
            try:
                target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                return {
                    "error": "Invalid date format. Use 'YYYY-MM-DD'.",
                    "code": "INVALID_DATE_FORMAT"
                }, 400

            # Find assigned medicine for user
            user_med_map = UserMedMap.query.filter_by(user_id=user_id, medicine_id=medicine_id).first()
            if not user_med_map:
                return {
                    "error": "Medicine assignment not found.",
                    "code": "MEDICINE_ASSIGNMENT_NOT_FOUND"
                }, 404

            # Find status entry by date
            status = Status.query.filter_by(user_med_map_id=user_med_map.id, date=target_date).first()
            if not status:
                return {
                    "error": "No status entry found for this date.",
                    "code": "STATUS_NOT_FOUND"
                }, 404

            return {
                "medicine_id": medicine_id,
                "date": target_date.isoformat(),
                "statuses": {
                    "breakfast_before": status.breakfast_before,
                    "breakfast_after": status.breakfast_after,
                    "lunch_before": status.lunch_before,
                    "lunch_after": status.lunch_after,
                    "dinner_before": status.dinner_before,
                    "dinner_after": status.dinner_after
                }
            }, 200
        
        # Database or ORM-related failures
        except SQLAlchemyError as e:
            return {
                "error": "Database error occurred while fetching medicine status.",
                "code": "DB_ERROR",
                "details": str(e)
            }, 500

        # Unexpected errors
        except Exception as e:
            return {
                "error": "An unexpected error occurred.",
                "code": "INTERNAL_SERVER_ERROR",
                "details": str(e)
            }, 500
        
@sc.route("/status-report", methods=["POST"])
class StatusReport(Resource):
    @jwt_required()
    @sc.expect(report_model, validate=True)
    def post(self):
        """Get a report of statuses for a senior citizen."""
        try:
            user_role = current_user.role
            data = request.get_json()

            month = data.get("month")
            year = data.get("year")

            if month is None or year is None:
                return {
                    "error": "Month and year are required in request body.",
                    "code": "MONTH_YEAR_REQUIRED"
                }, 400

            # Determine user_id based on role
            if user_role == "senior_citizen":
                user_id = current_user.id
            elif user_role == "care_giver":
                user_id = data.get("user_id")
                if not user_id:
                    return {
                        "error": "Missing 'user_id' (senior citizen ID) for caregiver.",
                        "code": "MISSING_SENIOR_ID"
                    }, 400

                # Validate caregiver-senior relationship
                is_approved = CaregiverSeniorMap.query.filter_by(
                    caregiver_id=current_user.id,
                    senior_id=user_id,
                    status='approved'
                ).first()

                if not is_approved:
                    return {
                        "error": "You are not an approved caregiver for this senior citizen.",
                        "code": "CAREGIVER_NOT_APPROVED"
                    }, 403
            else:
                return {
                    "error": "You are not authorized to access this resource.",
                    "code": "UNAUTHORIZED_ROLE"
                }, 403

            # Fetch all statuses for specified month and year
            statuses = db.session.query(Status).join(UserMedMap).filter(
                UserMedMap.user_id == user_id,
                extract('month', Status.date) == month,
                extract('year', Status.date) == year
            ).all()

            result = {}
            for status in statuses:
                date_str = status.date.strftime('%Y-%m-%d')
                slot_statuses = {
                    "breakfast_before": status.breakfast_before,
                    "breakfast_after": status.breakfast_after,
                    "lunch_before": status.lunch_before,
                    "lunch_after": status.lunch_after,
                    "dinner_before": status.dinner_before,
                    "dinner_after": status.dinner_after
                }
                taken = sum(1 for v in slot_statuses.values() if v is True)
                missed = sum(1 for v in slot_statuses.values() if v is False)

                result[date_str] = {
                    "taken": taken,
                    "missed": missed,
                    "details": slot_statuses
                }

            return result, 200

        # Handle DB errors
        except SQLAlchemyError as e:
            return {
                "error": "Database error occurred while fetching status report.",
                "code": "DB_ERROR",
                "details": str(e)
            }, 500

        # Handle all unexpected exceptions
        except Exception as e:
            return {
                "error": "An unexpected error occurred.",
                "code": "INTERNAL_SERVER_ERROR",
                "details": str(e)
            }, 500


# <------------------------------------Medicine Status for today------------------------------------>

@sc.route('/medicine-status-today')
class MedicineStatusToday(Resource):
    @jwt_required()
    @sc.expect(sc.model('SeniorInput', {
        'senior_citizen_id': fields.Integer(required=True, description='ID of the senior citizen')
    }), validate=True)
    def get(self):
        """Get the status of all medicines for a senior citizen for today."""
        try:
            user_role = current_user.role

            if user_role == "senior_citizen":
                user_id = current_user.id

            elif user_role == "care_giver":
                data = request.get_json()
                user_id = data.get("senior_citizen_id")

                if not user_id:
                    return {
                        "error": "Missing 'senior_citizen_id' for caregiver.",
                        "code": "MISSING_SENIOR_ID"
                    }, 400

                # Check caregiver-senior relationship
                is_approved = CaregiverSeniorMap.query.filter_by(
                    caregiver_id=current_user.id,
                    senior_id=user_id,
                    status='approved'
                ).first()
                if not is_approved:
                    return {
                        "error": "You are not an approved caregiver for this senior citizen.",
                        "code": "CAREGIVER_NOT_APPROVED"
                    }, 403

            else:
                return {
                    "error": "Unauthorized role.",
                    "code": "UNAUTHORIZED_ROLE"
                }, 403

            # Get medicine status for today
            ist = pytz.timezone('Asia/Kolkata')
            current_date = datetime.now(ist).date()

            user_meds = UserMedMap.query.filter_by(user_id=user_id).all()
            completed_meds = []
            pending_meds = []

            for um in user_meds:
                status = Status.query.filter(
                    Status.user_med_map_id == um.id,
                    func.date(Status.date) == current_date
                ).first()

                if not status:
                    continue

                slots = [
                    status.breakfast_before, status.breakfast_after,
                    status.lunch_before, status.lunch_after,
                    status.dinner_before, status.dinner_after
                ]

                valid_slots = [s for s in slots if s is not None]
                if not valid_slots:
                    continue

                med_info = {
                    'medicine_id': um.medicine_id,
                    'medicine_title': um.medicine.title,
                    'dosage': um.dosage
                }

                if all(valid_slots):
                    completed_meds.append(med_info)
                else:
                    pending_meds.append(med_info)

            return {
                'date': current_date.isoformat(),
                'completed_medicines': completed_meds,
                'pending_medicines': pending_meds
            }, 200

        except SQLAlchemyError as e:
            return {
                "error": "A database error occurred while retrieving today's medicine status.",
                "code": "DB_ERROR",
                "details": str(e)
            }, 500

        except Exception as e:
            return {
                "error": "An unexpected error occurred.",
                "code": "INTERNAL_SERVER_ERROR",
                "details": str(e)
            }, 500

#<------------------------------------------------------------------------------------------------------------------>

#<------------------------------------CRUD Operations for Medicine Reminder------------------------------------>
@sc.route('/add-medicine-reminder')
class AddMedicineReminder(Resource):
    @jwt_required()
    @sc.expect(medicine_reminder_model, validate=True)
    def post(self):
        """Add a new medicine reminder"""
        try:
            data = request.get_json()

            # Validate required fields (additional safeguard beyond `validate=True`)
            required_fields = ['user_med_map_id', 'reminder_time', 'notification_type', 'message']
            for field in required_fields:
                if field not in data:
                    return {
                        "error": f"'{field}' is a required field.",
                        "code": "MISSING_FIELD"
                    }, 400

            # Optional: check if user has permission (e.g., only caregivers or seniors can add reminders)
            # Example stub:
            # if current_user.role not in ['senior_citizen', 'care_giver']:
            #     return {"error": "You are not authorized to add reminders.", "code": "FORBIDDEN_ROLE"}, 403

            reminder = MedicineReminder(
                user_med_map_id=data['user_med_map_id'],
                reminder_time=data['reminder_time'],
                notification_type=data['notification_type'],
                message=data['message'],
                active=data.get('active', True)
            )

            db.session.add(reminder)
            db.session.commit()

            return {
                "message": "Reminder created successfully.",
                "id": reminder.id
            }, 201

        except SQLAlchemyError as e:
            db.session.rollback()
            return {
                "error": "A database error occurred while saving the reminder.",
                "code": "DB_ERROR",
                "details": str(e)
            }, 500

        except Exception as e:
            return {
                "error": "An unexpected error occurred.",
                "code": "INTERNAL_SERVER_ERROR",
                "details": str(e)
            }, 500
        
@sc.route('/specific-medicine-reminder')
class ViewMedicineReminder(Resource):
    @jwt_required()
    @sc.doc(params={
        'reminder_id': 'ID of the reminder to fetch'
    })
    def get(self):
        """View a specific medicine reminder by ID (query parameter)"""
        try:
            reminder_id = request.args.get('reminder_id', type=int)

            # Validate query parameter
            if not reminder_id:
                return {
                    "error": "Query parameter 'reminder_id' is required and must be an integer.",
                    "code": "MISSING_REMINDER_ID"
                }, 400

            reminder = MedicineReminder.query.get(reminder_id)

            # Check if reminder exists
            if not reminder:
                return {
                    "error": "Reminder not found for the given ID.",
                    "code": "REMINDER_NOT_FOUND"
                }, 404

            return {
                "id": reminder.id,
                "user_med_map_id": reminder.user_med_map_id,
                "reminder_time": str(reminder.reminder_time),
                "notification_type": reminder.notification_type,
                "message": reminder.message,
                "active": reminder.active
            }, 200

        except SQLAlchemyError as e:
            return {
                "error": "Database error occurred while retrieving the reminder.",
                "code": "DB_ERROR",
                "details": str(e)
            }, 500

        except Exception as e:
            return {
                "error": "An unexpected error occurred.",
                "code": "INTERNAL_SERVER_ERROR",
                "details": str(e)
            }, 500
        
@sc.route('/update-medicine-reminder')
class UpdateMedicineReminder(Resource):
    @jwt_required()
    @sc.expect(medicine_reminder_model, validate=True)
    def put(self):
        """Update a reminder using body data"""
        try:
            data = request.get_json()
            reminder_id = data.get('reminder_id')

            if not reminder_id:
                return {
                    "error": "Field 'reminder_id' is required in the request body.",
                    "code": "MISSING_REMINDER_ID"
                }, 400

            reminder = MedicineReminder.query.get(reminder_id)
            if not reminder:
                return {
                    "error": f"Reminder with ID {reminder_id} not found.",
                    "code": "REMINDER_NOT_FOUND"
                }, 404

            required_fields = ['user_med_map_id', 'reminder_time', 'notification_type', 'message']
            for field in required_fields:
                if field not in data:
                    return {
                        "error": f"'{field}' is a required field.",
                        "code": "MISSING_FIELD"
                    }, 400

            # Update reminder fields
            reminder.user_med_map_id = data['user_med_map_id']
            reminder.reminder_time = data['reminder_time']
            reminder.notification_type = data['notification_type']
            reminder.message = data['message']
            reminder.active = data.get('active', True)

            db.session.commit()

            return {
                "message": "Reminder updated successfully.",
                "id": reminder.id
            }, 200

        except SQLAlchemyError as e:
            db.session.rollback()  # Ensure DB state is clean on failure
            return {
                "error": "Database error occurred while updating the reminder.",
                "code": "DB_ERROR",
                "details": str(e)
            }, 500

        except Exception as e:
            return {
                "error": "An unexpected error occurred.",
                "code": "INTERNAL_SERVER_ERROR",
                "details": str(e)
            }, 500

@sc.route('/list-medicine-reminder')
class ListReminders(Resource):
    @jwt_required()
    @sc.doc(
        params={
            'user_med_map_id': 'ID of the User-Medicine mapping to fetch reminders for'
        },
        description='List all reminders for a specific user_med_map_id'
    )
    def get(self):
        """List all reminders for a specific user_med_map_id"""
        try:
            user_med_map_id = request.args.get('user_med_map_id', type=int)

            if not user_med_map_id:
                return {
                    "error": "Query parameter 'user_med_map_id' is required and must be an integer.",
                    "code": "MISSING_USER_MED_MAP_ID"
                }, 400

            reminders = MedicineReminder.query.filter_by(user_med_map_id=user_med_map_id).all()

            if not reminders:
                return {
                    "error": f"No reminders found for user_med_map_id {user_med_map_id}.",
                    "code": "REMINDERS_NOT_FOUND"
                }, 404

            return [{
                "id": r.id,
                "reminder_time": str(r.reminder_time),
                "notification_type": r.notification_type,
                "message": r.message,
                "active": r.active
            } for r in reminders], 200

        except SQLAlchemyError as e:
            return {
                "error": "Database error occurred while fetching reminders.",
                "code": "DB_ERROR",
                "details": str(e)
            }, 500

        except Exception as e:
            return {
                "error": "An unexpected error occurred.",
                "code": "INTERNAL_SERVER_ERROR",
                "details": str(e)
            }, 500

#<------------------------------------------------------------------------------------------------------------------->


# <------------------------------------Medicine Status for today------------------------------------>

@sc.route('/send-reminder')
class SendMedicineReminder(Resource):
    @jwt_required()
    @sc.expect(send_reminder_model, validate=True)
    def post(self):
        """Send active reminders for a specific medicine"""
        try:
            data = request.get_json()
            user_id = data.get('user_id')
            medicine_id = data.get('medicine_id')

            # Validate required inputs
            if not user_id or not medicine_id:
                return {
                    "error": "Both 'user_id' and 'medicine_id' are required in the request body.",
                    "code": "MISSING_REQUIRED_FIELDS"
                }, 400

            # Check if user-med mapping exists
            user_med_map = UserMedMap.query.filter_by(user_id=user_id, medicine_id=medicine_id).first()
            if not user_med_map:
                return {
                    "error": "Medicine mapping for the user not found.",
                    "code": "USER_MED_MAPPING_NOT_FOUND"
                }, 404

            # Fetch active reminders
            reminders = MedicineReminder.query.filter_by(user_med_map_id=user_med_map.id, active=True).all()
            if not reminders:
                return {
                    "message": "No active reminders found for this medicine.",
                    "medicine_id": medicine_id,
                    "user_id": user_id,
                    "reminders": [],
                    "code": "NO_ACTIVE_REMINDERS"
                }, 200

            # Compose and log/send reminders
            medicine_title = user_med_map.medicine.title if user_med_map.medicine else "Unknown Medicine"
            sent_reminders = []
            for reminder in reminders:
                message = reminder.message or f"Reminder to take {medicine_title} at {reminder.reminder_time}"
                # Simulated notification send (e.g. via email/SMS/push)
                print(f"[{reminder.notification_type.upper()}] To user {user_id}: {message}")

                sent_reminders.append({
                    "type": reminder.notification_type,
                    "time_slot": str(reminder.reminder_time),
                    "message": message
                })

            return {
                "status": "Reminders sent",
                "medicine_id": medicine_id,
                "user_id": user_id,
                "reminders": sent_reminders
            }, 200

        except SQLAlchemyError as e:
            return {
                "error": "Database error occurred while sending reminders.",
                "code": "DB_ERROR",
                "details": str(e)
            }, 500

        except Exception as e:
            return {
                "error": "An unexpected error occurred.",
                "code": "INTERNAL_SERVER_ERROR",
                "details": str(e)
            }, 500
# <-------------------------------------------------------------------------------------------------------------->

# <-------------------------------------SOS--------------------------------------------------------------------->

@sc.route('/send-sos')
class SendSOS(Resource):
    @jwt_required()
    def post(self):
        """Send SOS message from a senior to all mapped caregivers"""
        try:
            user_id = get_jwt_identity()

            # Get the calling user
            senior = User.query.get(user_id)
            if not senior:
                return {
                    "error": "User not found.",
                    "code": "USER_NOT_FOUND"
                }, 404

            # Check user role
            if senior.role != 'senior_citizen':
                return {
                    "error": "Only senior citizens can send SOS alerts.",
                    "code": "FORBIDDEN_ROLE"
                }, 403

            # Find all approved caregiver mappings
            caregiver_mappings = CaregiverSeniorMap.query.filter_by(
                senior_id=user_id,
                status='approved'
            ).all()

            if not caregiver_mappings:
                return {
                    "message": "No caregivers mapped to this user.",
                    "code": "NO_CAREGIVER_FOUND"
                }, 404

            sos_message = f"SOS Alert! {senior.first_name} {senior.last_name} needs immediate assistance!"

            sent_alerts = []
            for mapping in caregiver_mappings:
                caregiver = User.query.get(mapping.caregiver_id)
                if caregiver:
                    # Simulate sending alert (e.g. via message gateway)
                    print(f"Sending SOS to caregiver {caregiver.username}: {sos_message}")

                    sent_alerts.append({
                        "caregiver_id": caregiver.id,
                        "caregiver_name": f"{caregiver.first_name} {caregiver.last_name}",
                        "message": sos_message
                    })

            return {
                "status": "SOS sent successfully",
                "alerts_sent": sent_alerts
            }, 200

        except SQLAlchemyError as e:
            return {
                "error": "Database error occurred while sending SOS.",
                "code": "DB_ERROR",
                "details": str(e)
            }, 500

        except Exception as e:
            return {
                "error": "An unexpected error occurred.",
                "code": "INTERNAL_SERVER_ERROR",
                "details": str(e)
            }, 500
    
# <------------------------------------------------------------------------------------------------------------->

# <-------------------------------------Display all medicines of an elderly and caregiver------------------------------------>
@sc.route('/medicines')
class AllMedicines(Resource):
    @jwt_required()
    def get(self):
        """Get all medicines for logged-in user (senior or caregiver)"""
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)

            if not user:
                return {
                    "error": "User not found.",
                    "code": "USER_NOT_FOUND"
                }, 404

            # Initialize container
            mappings = []

            if user.role == 'senior':
                mappings = UserMedMap.query.filter_by(user_id=user_id).all()

            elif user.role == 'caregiver':
                senior_ids = db.session.query(CaregiverSeniorMap.senior_id).filter_by(
                    caregiver_id=user_id, status='approved'
                ).all()
                senior_ids = [sid[0] for sid in senior_ids]

                if not senior_ids:
                    return {
                        "error": "No senior citizens mapped to this caregiver.",
                        "code": "NO_SENIORS_ASSIGNED"
                    }, 404

                mappings = UserMedMap.query.filter(UserMedMap.user_id.in_(senior_ids)).all()

            else:
                return {
                    "error": "User role not permitted to access medicines.",
                    "code": "FORBIDDEN_ROLE"
                }, 403

            if not mappings:
                return {
                    "message": "No medicines found.",
                    "code": "NO_MEDICINES_FOUND"
                }, 200

            result = []
            for map in mappings:
                med = map.medicine
                assigned_user = map.user

                result.append({
                    "medicine_id": med.id if med else None,
                    "title": med.title if med else "",
                    "description": med.description if med else "",
                    "image": med.image if med else "",
                    "dosage": map.dosage,
                    "start_date": map.start_date.isoformat() if map.start_date else None,
                    "end_date": map.end_date.isoformat() if map.end_date else None,
                    "assigned_to": f"{assigned_user.first_name} {assigned_user.last_name}" if assigned_user else "Unknown"
                })

            return {
                "medicines": result
            }, 200

        except SQLAlchemyError as e:
            return {
                "error": "Database error occurred while fetching medicines.",
                "code": "DB_ERROR",
                "details": str(e)
            }, 500

        except Exception as e:
            return {
                "error": "An unexpected error occurred.",
                "code": "INTERNAL_SERVER_ERROR",
                "details": str(e)
            }, 500

#<------------------------------------------------------------------------------------------------------------->

# <-------------------------------------Senior citizen approve caregiver request------------------------------------>

@sc.route('/approve-caregiver')
class ApproveCaregiver(Resource):
    @jwt_required()
    @sc.expect(sc.model('ApproveCaregiver', {
        'caregiver_id': fields.Integer(required=True, description='ID of the caregiver to approve'),
        'approve': fields.Boolean(required=True, description='True to approve, False to deny')
    }))
    def post(self):
        """Senior approves or denies caregiver connection request"""
        try:
            data = request.get_json()
            caregiver_id = data.get('caregiver_id')
            approve = data.get('approve')

            if caregiver_id is None or approve is None:
                return {
                    "error": "'caregiver_id' and 'approve' are required fields.",
                    "code": "MISSING_FIELDS"
                }, 400

            senior_id = get_jwt_identity()
            senior = User.query.get(senior_id)

            if not senior or senior.role != 'senior_citizen':
                return {
                    "error": "Only senior citizens can approve caregiver requests.",
                    "code": "FORBIDDEN_ROLE"
                }, 403

            relation = CaregiverSeniorMap.query.filter_by(
                caregiver_id=caregiver_id, senior_id=senior_id
            ).first()

            if not relation:
                return {
                    "error": "No pending request found from this caregiver.",
                    "code": "RELATION_NOT_FOUND"
                }, 404

            if relation.status == 'approved' and approve:
                return {
                    "message": "Caregiver request already approved.",
                    "code": "ALREADY_APPROVED"
                }, 200

            relation.status = 'approved' if approve else 'rejected'
            db.session.commit()

            return {
                "message": f"Caregiver request {'approved' if approve else 'rejected'} successfully.",
                "caregiver_id": caregiver_id,
                "status": relation.status
            }, 200

        except SQLAlchemyError as e:
            db.session.rollback()
            return {
                "error": "Database error occurred while processing the caregiver approval.",
                "code": "DB_ERROR",
                "details": str(e)
            }, 500

        except Exception as e:
            return {
                "error": "An unexpected error occurred.",
                "code": "INTERNAL_SERVER_ERROR",
                "details": str(e)
            }, 500

# <------------------------------------------------------------------------------------------------------------->

# <-------------------------------------Caregiver send request to senior citizen------------------------------------>

@sc.route('/request-senior')
class RequestSenior(Resource):
    @jwt_required()
    @sc.expect(sc.model('RequestSenior', {
        'senior_id': fields.Integer(required=True, description="ID of the senior citizen to request")
    }), validate=True)
    def post(self):
        """Caregiver sends a request to a senior citizen"""
        try:
            data = request.get_json()
            senior_id = data.get('senior_id')
            caregiver_id = get_jwt_identity()

            caregiver = User.query.get(caregiver_id)
            if not caregiver or caregiver.role != 'care_giver':
                return {
                    "error": "Only caregivers can send requests.",
                    "code": "FORBIDDEN_ROLE"
                }, 403

            senior = User.query.get(senior_id)
            if not senior or senior.role != 'senior_citizen':
                return {
                    "error": "Target user is not a valid senior citizen.",
                    "code": "INVALID_SENIOR"
                }, 404

            # Check for existing caregiver-senior relationship
            relation = CaregiverSeniorMap.query.filter_by(
                caregiver_id=caregiver_id,
                senior_id=senior_id
            ).first()

            if relation:
                if relation.status == 'pending':
                    return {
                        "message": "Request already sent and pending approval.",
                        "code": "REQUEST_PENDING"
                    }, 200
                elif relation.status == 'approved':
                    return {
                        "message": "You are already approved as a caregiver for this senior.",
                        "code": "ALREADY_APPROVED"
                    }, 200
                elif relation.status == 'rejected':
                    return {
                        "message": "Your previous request was rejected.",
                        "code": "REQUEST_REJECTED"
                    }, 200

            # Create new caregiver-senior relationship
            new_relation = CaregiverSeniorMap(
                caregiver_id=caregiver_id,
                senior_id=senior_id,
                status='pending'
            )
            db.session.add(new_relation)
            db.session.commit()

            return {
                "message": "Request sent to senior citizen successfully.",
                "senior_id": senior_id,
                "status": "pending"
            }, 201

        except SQLAlchemyError as e:
            db.session.rollback()
            return {
                "error": "Database error occurred while creating request.",
                "code": "DB_ERROR",
                "details": str(e)
            }, 500

        except Exception as e:
            return {
                "error": "An unexpected error occurred.",
                "code": "INTERNAL_SERVER_ERROR",
                "details": str(e)
            }, 500
    

# <-------------------------------------Admin approval for new medicines------------------------------------>

@sc.route('/admin/medicine/approval')
class MedicineApproval(Resource):
    @jwt_required()
    @sc.expect(sc.model('MedicineApproval', {
        'medicine_id': fields.Integer(required=True, description='ID of the medicine to act upon'),
        'approve': fields.Boolean(required=True, description='True to approve, False to reject')
    }), validate=True)
    def post(self):
        """Admin approves or rejects a medicine"""
        try:
            user_id = get_jwt_identity()
            admin = User.query.get(user_id)

            if not admin or admin.role != 'admin':
                return {
                    "error": "Only admins can perform this action.",
                    "code": "FORBIDDEN_ROLE"
                }, 403

            data = request.get_json()
            medicine_id = data.get('medicine_id')
            approve = data.get('approve')

            medicine = Medicine.query.get(medicine_id)
            if not medicine:
                return {
                    "error": "Medicine not found.",
                    "code": "MEDICINE_NOT_FOUND"
                }, 404

            # Handle already final statuses
            if medicine.status == 'approved' and approve:
                return {
                    "error": "Medicine is already approved.",
                    "code": "ALREADY_APPROVED"
                }, 400

            if medicine.status == 'rejected' and not approve:
                return {
                    "error": "Medicine is already rejected.",
                    "code": "ALREADY_REJECTED"
                }, 400

            # Apply approval/rejection
            medicine.status = 'approved' if approve else 'rejected'
            medicine.is_approved = approve

            db.session.commit()

            return {
                "message": f"Medicine has been {medicine.status}.",
                "medicine_id": medicine.id,
                "status": medicine.status,
                "approved": medicine.is_approved
            }, 200

        except SQLAlchemyError as e:
            db.session.rollback()
            return {
                "error": "Database error occurred while updating medicine approval.",
                "code": "DB_ERROR",
                "details": str(e)
            }, 500

        except Exception as e:
            return {
                "error": "An unexpected error occurred.",
                "code": "INTERNAL_SERVER_ERROR",
                "details": str(e)
            }, 500

# <------------------------------------------------------------------------------------------------------------->

# <-------------------------------------List All Pending Medicines------------------------------------>

@sc.route('/admin/medicine/pending')
class PendingMedicines(Resource):
    @jwt_required()
    def get(self):
        """List all unapproved medicines (admin only)"""
        try:
            user_id = get_jwt_identity()
            admin = User.query.get(user_id)

            if not admin or admin.role != 'admin':
                return {
                    "error": "Only admins can view pending medicines.",
                    "code": "FORBIDDEN_ROLE"
                }, 403

            pending = Medicine.query.filter_by(status="pending").all()

            if not pending:
                return {
                    "message": "No pending medicines found.",
                    "medicines": [],
                    "code": "NO_PENDING_MEDICINES"
                }, 200

            result = [{
                "id": m.id,
                "title": m.title,
                "description": m.description,
                "user_id": m.user_id,
                "created_at": m.created_at.isoformat() if m.created_at else None
            } for m in pending]

            return {
                "pending_medicines": result,
                "count": len(result)
            }, 200

        except SQLAlchemyError as e:
            return {
                "error": "A database error occurred while fetching pending medicines.",
                "code": "DB_ERROR",
                "details": str(e)
            }, 500

        except Exception as e:
            return {
                "error": "An unexpected error occurred.",
                "code": "INTERNAL_SERVER_ERROR",
                "details": str(e)
            }, 500

# <-------------------------------------List All Rejected Medicines------------------------------------>
@sc.route('/admin/medicine/rejected')
class RejectedMedicines(Resource):
    @jwt_required()
    def get(self):
        """List all rejected medicines (admin only)"""
        try:
            user_role = current_user.role

            if user_role != 'admin':
                return {
                    "error": "Only admins can view rejected medicines.",
                    "code": "FORBIDDEN_ROLE"
                }, 403

            rejected = Medicine.query.filter_by(status="rejected").all()

            if not rejected:
                return {
                    "message": "No rejected medicines found.",
                    "rejected_medicines": [],
                    "code": "NO_REJECTED_MEDICINES"
                }, 200

            result = [{
                "id": m.id,
                "title": m.title,
                "description": m.description,
                "user_id": m.user_id,
                "created_at": m.created_at.isoformat() if m.created_at else None
            } for m in rejected]

            return {
                "rejected_medicines": result,
                "count": len(result)
            }, 200

        except SQLAlchemyError as e:
            return {
                "error": "Database error occurred while fetching rejected medicines.",
                "code": "DB_ERROR",
                "details": str(e)
            }, 500

        except Exception as e:
            return {
                "error": "An unexpected error occurred.",
                "code": "INTERNAL_SERVER_ERROR",
                "details": str(e)
            }, 500

 # <------------------------------------------------------------------------------------------------------------->

# <----------------------------------------------------------------------------------------------------->

# <-------------------------------------Upcoming medications------------------------------------>
@sc.route('/upcoming-medications')
class UpcomingMedications(Resource):
    @jwt_required()
    def get(self):
        """Get upcoming medications before scheduled times for the logged-in senior or approved seniors for caregiver"""
        try:
            user = current_user
            now = datetime.now(ZoneInfo("Asia/Kolkata"))
            current_hour = now.hour
            today = now.date()

            # Determine which slots should be shown
            slots = []
            if 4 <= current_hour < 10:
                slots.extend(['breakfast_before', 'breakfast_after'])
            if 10 <= current_hour < 15:
                slots.extend(['lunch_before', 'lunch_after'])
            if 16 <= current_hour < 23:
                slots.extend(['dinner_before', 'dinner_after'])

            if not slots:
                return {
                    "message": "No upcoming medications for the current time window.",
                    "upcoming_medications": [],
                    "code": "NO_ACTIVE_TIME_SLOT"
                }, 200

            result = []

            def get_meds_for_user(user_id):
                return UserMedMap.query.join(Medicine).filter(
                    UserMedMap.user_id == user_id,
                    UserMedMap.start_date <= today,
                    UserMedMap.end_date >= today
                ).all()

            if user.role == 'senior_citizen':
                meds = get_meds_for_user(user.id)
                result = filter_meds_by_time(meds, slots)

            elif user.role == 'care_giver':
                approved_seniors = CaregiverSeniorMap.query.filter_by(
                    caregiver_id=user.id,
                    status="approved"
                ).with_entities(CaregiverSeniorMap.senior_id).all()

                senior_ids = [s[0] for s in approved_seniors]

                if not senior_ids:
                    return {
                        "message": "No senior citizens mapped to this caregiver.",
                        "code": "NO_SENIORS_ASSIGNED",
                        "upcoming_medications": []
                    }, 200

                for sid in senior_ids:
                    meds = get_meds_for_user(sid)
                    result.extend(filter_meds_by_time(meds, slots, sid))

            else:
                return {
                    "error": "You are not authorized to access this resource.",
                    "code": "UNAUTHORIZED_ROLE"
                }, 403

            if not result:
                return {
                    "message": "No upcoming medications found.",
                    "code": "NO_UPCOMING_MEDICATIONS"
                }, 404

            return {
                "upcoming_medications": result,
                "count": len(result)
            }, 200

        except SQLAlchemyError as e:
            return {
                "error": "A database error occurred while fetching upcoming medications.",
                "code": "DB_ERROR",
                "details": str(e)
            }, 500
        except Exception as e:
            return {
                "error": "An unexpected error occurred.",
                "code": "INTERNAL_SERVER_ERROR",
                "details": str(e)
            }, 500
        
def filter_meds_by_time(meds, valid_slots, user_id=None):
    """Filter medicine slots by upcoming 3-hour window"""
    upcoming = []
    for med in meds:
        for slot in valid_slots:
            if getattr(med, slot, False):  # Defensive valid attribute check
                upcoming.append({
                    "user_id": user_id,
                    "medicine_id": med.medicine_id,
                    "medicine_title": med.medicine.title,
                    "dosage": med.dosage,
                    "start_date": med.start_date.isoformat(),
                    "end_date": med.end_date.isoformat(),
                    "reminder_slot": slot.replace('_', ' ').capitalize()
                })
    return upcoming

# <-------------------------------------Today's medication for Senior Citizen------------------------------------>

@sc.route('/todays-medications')
class TodaysMedications(Resource):
    @jwt_required()
    def get(self):
        """Get today's medications for the logged-in senior citizen"""
        try:
            user_id = current_user.id
            user = User.query.get(user_id)

            if not user or user.role != 'senior_citizen':
                return {
                    "error": "Only senior citizens can access this endpoint.",
                    "code": "FORBIDDEN_ROLE"
                }, 403

            today = datetime.utcnow().date()

            # Query active medicine assignments for today
            assignments = UserMedMap.query.filter(
                UserMedMap.user_id == user_id,
                UserMedMap.start_date <= today,
                UserMedMap.end_date >= today
            ).all()

            if not assignments:
                return {
                    "message": "No medications scheduled for today.",
                    "medications": [],
                    "code": "NO_TODAYS_MEDICINES"
                }, 404

            result = []
            for assign in assignments:
                med = assign.medicine
                if not med:
                    continue # Defensive safety for broken assignment

                slots = [
                    ("Before Breakfast", assign.breakfast_before),
                    ("After Breakfast", assign.breakfast_after),
                    ("Before Lunch", assign.lunch_before),
                    ("After Lunch", assign.lunch_after),
                    ("Before Dinner", assign.dinner_before),
                    ("After Dinner", assign.dinner_after)
                ]

                for slot_name, is_active in slots:
                    if is_active:
                        result.append({
                            "medicine_name": med.title,
                            "dosage": assign.dosage,
                            "time": slot_name
                        })

            if not result:
                return {
                    "message": "No time slots scheduled for today’s medications.",
                    "code": "NO_ACTIVE_SLOTS",
                    "medications": []
                }, 200

            return {
                "date": today.isoformat(),
                "medications": result,
                "count": len(result)
            }, 200

        except SQLAlchemyError as e:
            return {
                "error": "Database error while fetching today’s medications.",
                "code": "DB_ERROR",
                "details": str(e)
            }, 500

        except Exception as e:
            return {
                "error": "An unexpected error occurred.",
                "code": "INTERNAL_SERVER_ERROR",
                "details": str(e)
            }, 500

# <------------------------------------------------------------------------------------------------------------->

# <-------------------------------------Marking Medicines as taken------------------------------------>

@sc.route("/mark-medicine-taken", methods=["PUT"])
class MarkMedicineTaken(Resource):
    @jwt_required()
    @sc.expect(sc.model('MarkMedicineTaken', {
        'medicine_id': fields.Integer(required=True),
        'slot': fields.String(required=True, example="breakfast_before"),
    }), validate=True)
    def put(self):
        """Mark a medicine as taken for the logged-in senior citizen"""
        user_id = get_jwt_identity()
        data = request.get_json()
        
        medicine_id = data.get("medicine_id")
        slot = data.get("slot")  
        if not all([medicine_id, slot]):
            return {"error": "medicine_id and slot are required."}, 400

        if slot not in [
            "breakfast_before", "breakfast_after",
            "lunch_before", "lunch_after",
            "dinner_before", "dinner_after"
        ]:
            return {"error": "Invalid slot value."}, 400

        user_med_map = UserMedMap.query.filter_by(user_id=user_id,medicine_id=medicine_id).first()
        if not user_med_map:
            return {"error": "Medicine assignment not found."}, 404
        status = Status.query.filter(Status.user_med_map_id==user_med_map.id,func.date(Status.date)==datetime.utcnow().date()).first()
        if not status:
            return {"error": "Status entry not found for this date."}, 404
        setattr(status, slot, True)
        try:
            db.session.commit()
            return {"message": f"Marked {slot} as taken for {datetime.utcnow().date()}"}, 200
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

# <------------------------------------------------------------------------------------------------------------->

# <-------------------------------------Daily Health Entry------------------------------------>

@sc.route("/health-entry", methods=["POST"])
class HealthEntry(Resource):
    @jwt_required()
    @sc.expect(sc.model('HealthEntry', {
        'bp_systolic': fields.Integer(required=True),
        'bp_diastolic': fields.Integer(required=True),
        'sugar_level': fields.Float(required=True)
    }), validate=True)
    def post(self):
        """Record a daily health entry for the logged-in senior citizen"""
        user_id = get_jwt_identity()
        data = request.get_json()
        try:
            today = datetime.utcnow().date()
            existing_entry = DailyHealthEntry.query.filter_by(user_id=user_id, date=today).first()
            if existing_entry:
                return {"error": "Health entry already exists for today."}, 400
            new_entry = DailyHealthEntry(
                user_id=user_id,
                date=today,
                bp_systolic=data.get("bp_systolic"),
                bp_diastolic=data.get("bp_diastolic"),
                sugar_level=data.get("sugar_level")
            )
            db.session.add(new_entry)
            db.session.commit()
            return {"message": "Today's health entry recorded successfully."}, 201
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

# <------------------------------------------------------------------------------------------------------------->
