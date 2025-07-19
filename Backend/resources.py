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
    'image': fields.String(required=False),
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
@sc.doc(description="Verifies the validity of a JWT token and returns its claims.")
class VerifyToken(Resource):
    
    def get(self):
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
@sc.doc(description="Allows a user to update their own profile details.")
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
@sc.doc(description="Creates a new medicine entry in the system.")
class CreateMedicine(Resource):
    @jwt_required()
    @sc.expect(create_medicine_model, validate=True)
    def post(self):
        """Create new medicine entry"""
        data = request.get_json()
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        status = "approved" if user and user.role == "admin" else "pending"

        medicine = Medicine(
            title=data['title'],
            description=data['description'],
            user_id=user_id,
            image=data.get('image'),
            status=status
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
@sc.doc(description="Retrieves all approved medicines.")
class AllMedicineNames(Resource):
    def get(self):
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
@sc.doc(description="Updates an existing medicine entry by its ID (admin only).")
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
@sc.doc(description="Deletes a medicine entry by its ID (admin only).")
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
@sc.doc(description="Assigns a medicine to a senior citizen or by a caregiver to their mapped senior.")
class AssignMedicine(Resource):
    @jwt_required()
    @sc.expect(assign_medicine_model, validate=True)
    def post(self):
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
@sc.doc(description="Unassigns a medicine from a senior citizen (by themselves or their caregiver).")
class UnassignMedicine(Resource):
    @jwt_required()
    @sc.expect(unassign_medicine_model, validate=True)
    def delete(self):
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
@sc.doc(description="Retrieves all medicines assigned to the logged-in senior citizen.")
class MyMedicines(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        user_role = current_user.role

        if (user_role != "senior_citizen"):
            return {"error": "You are not authorized to access this resource."}, 403
        

        user_meds = UserMedMap.query.filter_by(user_id=user_id).all()
        result = []
        for um in user_meds:
            med = um.medicine
            # Find which slots are assigned at least once
            assigned_slots = set()
            for status in um.statuses:
                if status.breakfast_before is not None:
                    assigned_slots.add("breakfast_before")
                if status.breakfast_after is not None:
                    assigned_slots.add("breakfast_after")
                if status.lunch_before is not None:
                    assigned_slots.add("lunch_before")
                if status.lunch_after is not None:
                    assigned_slots.add("lunch_after")
                if status.dinner_before is not None:
                    assigned_slots.add("dinner_before")
                if status.dinner_after is not None:
                    assigned_slots.add("dinner_after")
            result.append({
                "medicine_id": med.id,
                "title": med.title,
                "description": med.description,
                "dosage": um.dosage,
                "start_date": um.start_date.isoformat(),
                "end_date": um.end_date.isoformat(),
                "image": med.image,
                "is_approved": med.is_approved,
                "assigned_slots": list(assigned_slots)
            })
        return {"medicines": result}, 200

# <---------------------------------------------------------------------------------------------------------------->

# <------------------------------------Getting Status of medicine------------------------------------>

# getting medicine status
@sc.route("/medicine-status/<int:medicine_id>", methods=["GET"])
@sc.doc(description="Gets the status of a specific medicine for a user on a given date.")
class MedicineStatus(Resource):
    @jwt_required()
    @sc.doc(params={
    'date': 'Date in YYYY-MM-DD format (as query parameter)'
    })

    def get(self, medicine_id):
        user_id = get_jwt_identity()
        date_str = request.args.get('date')
        if not date_str:
            return {"error": "Date is required in 'YYYY-MM-DD' format as a query parameter."}, 400
        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return {"error": "Invalid date format. Use 'YYYY-MM-DD'."}, 400
        user_med_map = UserMedMap.query.filter_by(user_id=user_id, medicine_id=medicine_id).first()
        if not user_med_map:
            return {"error": "Medicine assignment not found."}, 404
        status = Status.query.filter_by(user_med_map_id=user_med_map.id, date=target_date).first()

        if not status:
            return {"error": "No status entry found for this date."}, 404
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

# TO get report of medicine status
@sc.route("/status-report", methods=["POST"])
@sc.doc(description="Generates a monthly medicine status report for a senior citizen or by a caregiver for their mapped senior.")
class StatusReport(Resource):
    @jwt_required()
    @sc.expect(report_model, validate=True)
    def post(self):
        # user_id = get_jwt_identity()
        user_role = current_user.role
        data = request.get_json()
        month = data.get("month")
        year = data.get("year")

        if(user_role == "senior_citizen"):
            user_id = current_user.id
        elif user_role == "care_giver":
            user_id = data.get("user_id")
            if not user_id:
                return {"error": "Missing 'senior citizen id' for caregiver"}, 400
            # Check caregiver-senior relationship
            is_approved = CaregiverSeniorMap.query.filter_by(
                caregiver_id=current_user.id,
                senior_id=user_id,
                status='approved'
                ).first()
            
            if not is_approved:
                return {"error": "You are not an approved caregiver for this senior citizen."}, 403
            
        if month is None or year is None:
            return {"error": "Month and year are required in JSON body."}, 400

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


# <------------------------------------Medicine Status for today------------------------------------>

# Medicine status for today
@sc.route('/medicine-status-today')
@sc.doc(description="Retrieves today's completed and pending medicines for a senior citizen (or by caregiver for their mapped senior).")
class MedicineStatusToday(Resource):
    @jwt_required()
    @sc.expect(sc.model('SeniorInput', {
        'senior_citizen_id': fields.Integer(required=True, description='ID of the senior citizen')
    }), validate=True)

    def get(self):
        # user_id = get_jwt_identity()
        user_role = current_user.role
        if(user_role == "senior_citizen"):
            user_id = current_user.id

        elif user_role == "care_giver":
            data = request.get_json()
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
            if all(valid_slots):
                completed_meds.append({
                    'medicine_id': um.medicine_id,
                    'medicine_title': um.medicine.title,
                    'dosage': um.dosage
                })
            else:
                pending_meds.append({
                    'medicine_id': um.medicine_id,
                    'medicine_title': um.medicine.title,
                    'dosage': um.dosage
                })
        
        return {
            'date': current_date.isoformat(),
            'completed_medicines': completed_meds,
            'pending_medicines': pending_meds
        }, 200

#<------------------------------------------------------------------------------------------------------------------>

#<------------------------------------CRUD Operations for Medicine Reminder------------------------------------>

# Create Medicine Reminder
@sc.route('/add-medicine-reminder')
@sc.doc(description="Creates a new reminder for a specific medicine assignment.")
class AddMedicineReminder(Resource):
    @jwt_required()
    @sc.expect(medicine_reminder_model)
    def post(self):
        """Add a new medicine reminder"""
        data = request.json
        reminder = MedicineReminder(
            user_med_map_id=data['user_med_map_id'],
            reminder_time=data['reminder_time'],
            notification_type=data['notification_type'],
            message=data['message'],
            active=data.get('active', True)
        )
        db.session.add(reminder)
        db.session.commit()
        return {"message": "Reminder created", "id": reminder.id}, 201

# View a specific reminder
@sc.route('/specific-medicine-reminder')
@sc.doc(description="Retrieves a specific medicine reminder by its ID.")
class ViewMedicineReminder(Resource):
    @jwt_required()
    @sc.doc(params={
        'reminder_id': 'ID of the reminder mapping to fetch reminders for'
    })
    def get(self):
        """View a specific reminder by query param"""
        reminder_id = request.args.get('reminder_id', type=int)
        if not reminder_id:
            return {"error": "Reminder ID is required in query"}, 400

        reminder = MedicineReminder.query.get(reminder_id)
        if not reminder:
            return {"error": "Reminder not found"}, 404

        return {
            "id": reminder.id,
            "user_med_map_id": reminder.user_med_map_id,
            "reminder_time": reminder.reminder_time,
            "notification_type": reminder.notification_type,
            "message": reminder.message,
            "active": reminder.active
        }, 200

# Update a reminder
@sc.route('/update-medicine-reminder')
@sc.doc(description="Updates an existing medicine reminder.")
class UpdateMedicineReminder(Resource):
    @jwt_required()
    @sc.expect(medicine_reminder_model)
    def put(self):
        """Update a reminder using body data"""
        data = request.json
        reminder_id = data.get('reminder_id')
        if not reminder_id:
            return {"error": "Reminder ID is required in body"}, 400

        reminder = MedicineReminder.query.get(reminder_id)
        if not reminder:
            return {"error": "Reminder not found"}, 404

        reminder.user_med_map_id = data['user_med_map_id']
        reminder.reminder_time = data['reminder_time']
        reminder.notification_type = data['notification_type']
        reminder.message = data['message']
        reminder.active = data.get('active', True)

        db.session.commit()
        return {"message": "Reminder updated"}, 200

# Delete a reminder
@sc.route('/delete-medicine-reminder')
@sc.doc(description="Deletes a medicine reminder by its ID.")
class DeleteMedicineReminder(Resource):
    @jwt_required()
    @sc.doc(params={
        'id': 'ID of the reminder to delete'
    })
    def delete(self):
        """Delete a reminder via query parameter"""
        reminder_id = request.args.get('id', type=int)
        if not reminder_id:
            return {"error": "Reminder ID is required in query"}, 400

        reminder = MedicineReminder.query.get(reminder_id)
        if not reminder:
            return {"error": "Reminder not found"}, 404

        db.session.delete(reminder)
        db.session.commit()
        return {"message": "Reminder deleted"}, 200

# List all reminders for a specific user_med_map_id
@sc.route('/list-medicine-reminder')
@sc.doc(description="Lists all reminders for a specific user-medicine mapping.")
class ListReminders(Resource):
    @jwt_required()
    @sc.doc(params={
        'user_med_map_id': 'ID of the User-Medicine mapping to fetch reminders for'
    })
    def get(self):
        """List all reminders for a specific user_med_map_id"""
        user_med_map_id = request.args.get('user_med_map_id', type=int)
        if not user_med_map_id:
            return {"error": "user_med_map_id is required as a query parameter"}, 400

        reminders = MedicineReminder.query.filter_by(user_med_map_id=user_med_map_id).all()
        return [{
            "id": r.id,
            "reminder_time": r.reminder_time,
            "notification_type": r.notification_type,
            "message": r.message,
            "active": r.active
        } for r in reminders], 200

#<------------------------------------------------------------------------------------------------------------------->


# <------------------------------------Medicine Status for today------------------------------------>

# Send reminder for a specific medicine
@sc.route('/send-reminder')
@sc.doc(description="Sends all active reminders for a specific medicine to the user.")
class SendMedicineReminder(Resource):
    @jwt_required()
    @sc.expect(send_reminder_model, validate=True)
    def post(self):
        """Send active reminders for a specific medicine"""
        data = request.get_json()
        user_id = data.get('user_id')
        medicine_id = data.get('medicine_id')

        # Validate input
        if not medicine_id:
            return {"error": "medicine_id is required in the request body."}, 400

        # Check user-med-mapping
        user_med_map = UserMedMap.query.filter_by(user_id=user_id, medicine_id=medicine_id).first()
        if not user_med_map:
            return {"error": "Medicine mapping for the user not found."}, 404

        # Fetch active reminders
        reminders = MedicineReminder.query.filter_by(user_med_map_id=user_med_map.id, active=True).all()
        if not reminders:
            return {"message": "No active reminders found for this medicine."}, 200

        # Compose notifications
        medicine_title = user_med_map.medicine.title if user_med_map.medicine else "Unknown Medicine"
        sent_reminders = []
        for reminder in reminders:
            message = reminder.message or f"Reminder to take {medicine_title} at {reminder.reminder_time}"
            print(f"[{reminder.notification_type.upper()}] To user {user_id}: {message}")
            sent_reminders.append({
                "type": reminder.notification_type,
                "time_slot": reminder.reminder_time,
                "message": message
            })

        return {
            "status": "Reminders sent",
            "medicine_id": medicine_id,
            "user_id": user_id,
            "reminders": sent_reminders
        }, 200
# <-------------------------------------------------------------------------------------------------------------->

# <-------------------------------------SOS--------------------------------------------------------------------->

# Send SOS
@sc.route('/send-sos')
@sc.doc(description="Sends an SOS alert from a senior citizen to all their mapped caregivers.")
class SendSOS(Resource):
    @jwt_required()
    # @sc.doc(params={
    #     'caregiver_id': 'Mention the caregiver ID'
    # })
    def post(self):
        """Send SOS message from a senior to all mapped caregivers"""
        user_id = get_jwt_identity()

        # Get the senior user
        senior = User.query.get(user_id)
        if not senior:
            return {"error": "User not found."}, 404

        # Get all caregivers mapped to this senior
        caregiver_mappings = CaregiverSeniorMap.query.filter_by(senior_id=user_id).all()
        if not caregiver_mappings:
            return {"message": "No caregivers mapped to this user."}, 404

        sos_message = f"SOS Alert! {senior.first_name} {senior.last_name} needs immediate assistance!"

        sent_alerts = []
        for mapping in caregiver_mappings:
            caregiver = User.query.get(mapping.caregiver_id)
            if caregiver:
                # Simulate sending alert (e.g., email, SMS, etc.)
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
    
# <------------------------------------------------------------------------------------------------------------->

# <-------------------------------------Display all medicines of an elderly and caregiver------------------------------------>
@sc.route('/medicines')
@sc.doc(description="Retrieves all medicines for the logged-in user (senior or caregiver for their mapped seniors).")
class AllMedicines(Resource):
    @jwt_required()
    def get(self):
        """Get all medicines for logged-in user (elderly or caregiver)"""
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return {"error": "User not found."}, 404

        # If user is an elderly, return their medicines
        if user.role == 'senior':
            mappings = UserMedMap.query.filter_by(user_id=user_id).all()

        # If user is a caregiver, get medicines of all their mapped seniors
        elif user.role == 'caregiver':
            senior_ids = db.session.query(CaregiverSeniorMap.senior_id).filter_by(caregiver_id=user_id).all()
            senior_ids = [sid[0] for sid in senior_ids]
            mappings = UserMedMap.query.filter(UserMedMap.user_id.in_(senior_ids)).all()

        else:
            return {"error": "User role not permitted to access medicines."}, 403

        # Prepare response
        result = []
        for map in mappings:
            result.append({
                "medicine_id": map.medicine.id,
                "title": map.medicine.title,
                "description": map.medicine.description,
                "image": map.medicine.image,
                "dosage": map.dosage,
                "start_date": map.start_date.isoformat(),
                "end_date": map.end_date.isoformat(),
                "assigned_to": map.user.first_name + " " + map.user.last_name
            })

        return {"medicines": result}, 200

#<------------------------------------------------------------------------------------------------------------->

# <-------------------------------------Senior citizen approve caregiver request------------------------------------>

@sc.route('/approve-caregiver')
@sc.doc(description="Allows a senior citizen to approve or reject a caregiver's request.")
class ApproveCaregiver(Resource):
    @jwt_required()
    @sc.expect(sc.model('ApproveCaregiver', {
        'caregiver_id': fields.Integer(required=True),
        'approve': fields.Boolean(required=True)
    }))

    def post(self):
        """Senior approves caregiver request"""
        data = request.get_json()
        caregiver_id = data.get('caregiver_id')
        senior_id = get_jwt_identity()

        senior = User.query.get(senior_id)
        if not senior or senior.role != 'senior_citizen':

            return {"error": "Only senior citizens can approve requests."}, 403

        relation = CaregiverSeniorMap.query.filter_by(caregiver_id=caregiver_id, senior_id=senior_id).first()
        if not relation:
            return {"error": "No pending request found from this caregiver."}, 404

        if relation.status == 'approved':
            return {"message": "Request already approved."}, 200

        relation.status = 'approved'
        db.session.commit()

        return {"message": "Caregiver request approved successfully."}, 200

# <------------------------------------------------------------------------------------------------------------->

# <-------------------------------------Caregiver send request to senior citizen------------------------------------>

@sc.route('/request-senior')
@sc.doc(description="Allows a caregiver to send a request to a senior citizen for mapping.")
class RequestSenior(Resource):
    @jwt_required()
    @sc.expect(sc.model('RequestSenior', {
        'senior_id': fields.Integer(required=True)
    }), validate=True)
    def post(self):
        """Caregiver sends request to senior citizen"""
        data = request.get_json()
        senior_id = data.get('senior_id')
        caregiver_id = get_jwt_identity()

        caregiver = User.query.get(caregiver_id)
        if not caregiver or caregiver.role != 'care_giver':
            return {"error": "Only caregivers can send requests."}, 403

        senior = User.query.get(senior_id)
        if not senior or senior.role != 'senior_citizen':
            return {"error": "Target user is not a senior citizen."}, 404

        # Check if a request already exists
        relation = CaregiverSeniorMap.query.filter_by(caregiver_id=caregiver_id, senior_id=senior_id).first()
        if relation:
            if relation.status == 'pending':
                return {"message": "Request already sent and pending approval."}, 200
            elif relation.status == 'approved':
                return {"message": "You are already approved as a caregiver for this senior."}, 200
            elif relation.status == 'rejected':
                return {"message": "Your previous request was rejected."}, 200

        # Create new request
        new_relation = CaregiverSeniorMap(
            caregiver_id=caregiver_id,
            senior_id=senior_id,
            status='pending'
        )
        db.session.add(new_relation)
        db.session.commit()

        return {"message": "Request sent to senior citizen successfully."}, 201
    

# <-------------------------------------Admin approval for new medicines------------------------------------>

@sc.route('/admin/medicine/approval')
@sc.doc(description="Allows an admin to approve or reject a new medicine entry.")
class MedicineApproval(Resource):
    @jwt_required()
    @sc.expect(sc.model('MedicineApproval', {
        'medicine_id': fields.Integer(required=True, description='ID of the medicine to act upon'),
        'approve': fields.Boolean(required=True, description='True to approve, False to reject')
    }), validate=True)
    def post(self):
        """Admin approves or rejects a medicine"""

        data = request.get_json()
        medicine_id = data.get('medicine_id')
        approve = data.get('approve')

        medicine = Medicine.query.get(medicine_id)
        if not medicine:
            return {"error": "Medicine not found."}, 404
        
        if (medicine.status == "approved"):
            return {"error": "Medicine is already approved."}, 400
        elif (medicine.status == "rejected"):
            return {"error": "Medicine is already rejected."}, 400
        status_msg = "approved" if approve else "rejected"
        
        if status_msg == "approved":
            # Change the status of the medicine to 'approved' in Medicine table
            medicine.status = 'approved'
        else:
            # Change the status of the medicine to 'rejected' in Medicine table
            medicine.status = 'rejected'

        db.session.commit()
        
        return {"message": f"Medicine has been {status_msg}."}, 200

# <------------------------------------------------------------------------------------------------------------->

# <-------------------------------------List All Pending Medicines------------------------------------>

@sc.route('/admin/medicine/pending')
@sc.doc(description="Lists all medicines pending admin approval.")
class PendingMedicines(Resource):
    @jwt_required()
    def get(self):
        """List all unapproved medicines (admin only)"""
        user_id = get_jwt_identity()
        admin = User.query.get(user_id)

        if not admin or admin.role != 'admin':
            return {"error": "Only admins can view pending medicines."}, 403

        pending = Medicine.query.filter_by(status="pending").all()

        return {"medicines":[{
            "id": m.id,
            "title": m.title,
            "description": m.description,
            "user_id": m.user_id,
            "created_at": m.created_at.isoformat()
        } for m in pending]}, 200

# <-------------------------------------List All Rejected Medicines------------------------------------>
@sc.route('/admin/medicine/rejected')
@sc.doc(description="Lists all medicines rejected by the admin.")
class RejectedMedicines(Resource):
    @jwt_required()
    def get(self):
        """List all rejected medicines (admin only)"""
        user_role = current_user.role
        if user_role != 'admin':
            return {"error": "Only admins can view rejected medicines."}, 403
        rejected = Medicine.query.filter_by(status="rejected").all()
        return {"rejected_medicines": [{
            "id": m.id,
            "title": m.title,
            "description": m.description
        } for m in rejected]}

 # <------------------------------------------------------------------------------------------------------------->

# <----------------------------------------------------------------------------------------------------->

# <-------------------------------------Upcoming medications------------------------------------>
@sc.route('/upcoming-medications')
@sc.doc(description="Retrieves upcoming medications for the logged-in senior or for all mapped seniors of a caregiver, based on the current time slot.")
class UpcomingMedications(Resource):
    @jwt_required()
    def get(self):
        """Get upcoming medications before scheduled times for the logged-in senior or approved seniors for caregiver"""
        user = current_user
        now = datetime.now(ZoneInfo("Asia/Kolkata"))
        current_hour = now.hour
        today = now.date()

        # Determine current slot
        slots = []

        if 4 <= current_hour < 10:
            slots.extend(['breakfast_before', 'breakfast_after'])
        if 10 <= current_hour < 15:
            slots.extend(['lunch_before', 'lunch_after'])
        if 16 <= current_hour < 23:
            slots.extend(['dinner_before', 'dinner_after'])

        if not slots:
            return {"upcoming medications": []}, 200

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
            approved_seniors = CaregiverSeniorMap.query.filter_by(caregiver_id=user.id).with_entities(
                CaregiverSeniorMap.senior_id
            ).all()
            senior_ids = [s[0] for s in approved_seniors]
            for sid in senior_ids:
                meds = get_meds_for_user(sid)
                result.extend(filter_meds_by_time(meds, slots, sid))

        else:
            return {"error": "Unauthorized role"}, 403

        if (not result):
            return {"message": "No medicine found"}, 404
        return {"upcoming_medications": result}, 200


def filter_meds_by_time(meds, valid_slots, user_id=None):
    """Filter medicine slots by upcoming 3-hour window"""
    upcoming = []
    for med in meds:
        for slot in valid_slots:
            if getattr(med, slot):
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
@sc.doc(description="Retrieves all medications scheduled for today for the logged-in senior citizen.")
class TodaysMedications(Resource):
    @jwt_required()
    def get(self):
        """Get today's medications for the logged-in senior citizen"""
        user_id = current_user.id
        user = User.query.get(user_id)
        if not user or user.role != 'senior_citizen':
            return {"error": "Only senior citizens can access this endpoint."}, 403

        today = datetime.utcnow().date()
        # Get all medicine assignments for this user that are active today
        assignments = UserMedMap.query.filter(
            UserMedMap.user_id == user_id,
            UserMedMap.start_date <= today,
            UserMedMap.end_date >= today
        ).all()

        result = []
        for assign in assignments:
            med = assign.medicine
            # For each slot, check if it's set to True and add to the result
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
        return {"date": today.isoformat(), "medications": result}, 200

# <------------------------------------------------------------------------------------------------------------->
# <------------------------------------------------------------------------------------------------------------->

# <-------------------------------------Marking Medicines as taken------------------------------------>

@sc.route("/mark-medicine-taken", methods=["PUT"])
@sc.doc(description="Marks a specific medicine slot as taken for today for the logged-in user.")
class MarkMedicineTaken(Resource):
    @jwt_required()
    @sc.expect(sc.model('MarkMedicineTaken', {
        'medicine_id': fields.Integer(required=True),
        'slot': fields.String(required=True, example="breakfast_before"),
    }), validate=True)
    def put(self):
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
@sc.doc(description="Records a daily health entry (blood pressure and sugar level) for the logged-in user.")
class HealthEntry(Resource):
    @jwt_required()
    @sc.expect(sc.model('HealthEntry', {
        'bp_systolic': fields.Integer(required=True),
        'bp_diastolic': fields.Integer(required=True),
        'sugar_level': fields.Float(required=True)
    }), validate=True)
    def post(self):
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
@sc.route('/my-caregiver')
@sc.doc(description="Fetches the caregiver information for a senior citizen.")
class MyCaregiver(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if user.role != "senior_citizen":
            return {"error": "Unauthorized"}, 403
        # Get mapping with approved status
        map = CaregiverSeniorMap.query.filter_by(senior_id=user_id, status='approved').first()
        if not map:
            return {"caregiver": None}, 200

        caregiver = User.query.get(map.caregiver_id)
        return {
            "caregiver": {
                "firstName": caregiver.first_name,
                "lastName": caregiver.last_name,
                "username": caregiver.username
            }
        }, 200

@sc.route('/my-dependents')
@sc.doc(description="Retrieves all approved senior citizens (dependents) assigned to the logged-in caregiver.")
class MyDependents(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        user_role = current_user.role
        if user_role != 'care_giver':
            return {"error": "You are not authorized to access this resource."}, 403

        # Get all approved seniors linked to this caregiver
        mappings = CaregiverSeniorMap.query.filter_by(caregiver_id=user_id, status='approved').all()
        dependents = []
        for m in mappings:
            senior = User.query.get(m.senior_id)
            if senior:
                dependents.append({
                    "id": senior.id,
                    "firstName": senior.first_name,
                    "lastName": senior.last_name,
                    "username": senior.username
                })

        return {"dependents": dependents}, 200

from datetime import date, timedelta

@sc.route('/user-stats/<int:senior_id>')
@sc.doc(description="Returns medicine compliance and vital statistics.")
class UserStats(Resource):
    @jwt_required()
    def get(self, senior_id):
        uid = get_jwt_identity()
        me = User.query.get(uid)

        # Role-based access control
        if me.role == 'care_giver':
            mapping = CaregiverSeniorMap.query.filter_by(
                caregiver_id=uid, senior_id=senior_id, status='approved'
            ).first()
            if not mapping:
                return {"error": "Access denied"}, 403
        elif me.role != 'senior_citizen' or me.id != senior_id:
            return {"error": "Access denied"}, 403

        today = date.today()
        last_30_excluding_today = today - timedelta(days=30)

        meds = UserMedMap.query.filter_by(user_id=senior_id).all()
        stacked = {}

        for um in meds:
            name = um.medicine.title
            stacked.setdefault(name, {"taken": 0, "missed": 0, "total_assigned": 0})

            for s in um.statuses:
                status_date = s.date.date()
                if last_30_excluding_today <= status_date < today:
                    for slot in [
                        s.breakfast_before, s.breakfast_after,
                        s.lunch_before, s.lunch_after,
                        s.dinner_before, s.dinner_after
                    ]:
                        if slot is not None:
                            stacked[name]["total_assigned"] += 1
                            if slot:
                                stacked[name]["taken"] += 1
                            else:
                                stacked[name]["missed"] += 1

        # Vitals: last 7 days INCLUDING today
        vitals_start = today - timedelta(days=6)  # last 7 days including today
        entries = DailyHealthEntry.query.filter(
            DailyHealthEntry.user_id == senior_id,
            DailyHealthEntry.date >= vitals_start
        ).order_by(DailyHealthEntry.date).all()

        days = [e.date.strftime('%b %d') for e in entries]
        systolic = [e.bp_systolic for e in entries]
        diastolic = [e.bp_diastolic for e in entries]
        sugar = [e.sugar_level for e in entries]

        return {
            "medicineCompliance": {
                "labels": list(stacked.keys()),
                "taken": [v["taken"] for v in stacked.values()],
                "missed": [v["missed"] for v in stacked.values()]
            },
            "vitalsLast7": {
                "labels": days,
                "systolic": systolic,
                "diastolic": diastolic,
                "sugar": sugar
            }
        }, 200
