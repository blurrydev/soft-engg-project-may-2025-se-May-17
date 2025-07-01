// src/services/mockApi.js

// This file simulates a backend API and database.
// The data is stored in memory and will be consistent across all pages
// for the duration of the user's session.

// --- SIMULATED DATABASE TABLES ---

const db = {
  // All users, including dependents and caregivers
  users: [
    { id: 'dep_001', firstName: 'Eleanor', lastName: 'Vance', birthDate: '1958-05-15', relation: 'Mom' },
    { id: 'dep_002', firstName: 'Hugh', lastName: 'Crain', birthDate: '1955-11-20', relation: 'Dad' },
    { id: 'user_101', firstName: 'John', lastName: 'Doe' }, // Our Caregiver
  ],
  caregiverDependentMap: [
    { caregiverId: 'user_101', dependentId: 'dep_001' },
    { caregiverId: 'user_101', dependentId: 'dep_002' },
  ],
  medicines: [
    { id: 1, title: 'Lisinopril' }, { id: 2, title: 'Metformin' }, { id: 3, title: 'Atorvastatin' },
    { id: 4, title: 'Amlodipine' }, { id: 5, title: 'Albuterol' },
  ],
  userMedMaps: [
    { id: 101, userId: 'dep_001', medicineId: 1, dosage: '10mg', breakfast_after: true, start_date: '2024-01-01', end_date: '2025-12-31' },
    { id: 102, userId: 'dep_001', medicineId: 3, dosage: '20mg', dinner_after: true, start_date: '2024-01-01', end_date: '2025-12-31' },
    { id: 103, userId: 'dep_001', medicineId: 5, dosage: '5 mg', lunch_before: true, start_date: '2024-01-01', end_date: '2025-12-31' },
    { id: 104, userId: 'dep_002', medicineId: 2, dosage: '500mg', breakfast_after: true, dinner_after: true, start_date: '2024-01-01', end_date: '2025-12-31' },
    { id: 105, userId: 'dep_002', medicineId: 4, dosage: '5mg', lunch_before: true, start_date: '2024-01-01', end_date: '2025-12-31' },
  ],
};

// --- HELPER FUNCTIONS ---
const simulateDelay = (ms = 500) => new Promise(res => setTimeout(res, ms));

const calculateAge = (birthDate) => {
  if (!birthDate) return null;
  const today = new Date();
  const birth = new Date(birthDate);
  let age = today.getFullYear() - birth.getFullYear();
  const m = today.getMonth() - birth.getMonth();
  if (m < 0 || (m === 0 && today.getDate() < birth.getDate())) {
    age--;
  }
  return age;
};

// --- MOCK API ENDPOINT FUNCTIONS ---

// GET /api/dependents
export async function getDependentsList() {
  await simulateDelay(300);
  console.log(`[Mock API] GET /api/dependents`);
  // Return a copy to prevent direct mutation from components
  return [...db.users];
}

// DELETE /api/dependents/:userId
export async function deleteDependent(userId) {
  await simulateDelay(300);
  console.log(`[Mock API] DELETE /api/dependents/${userId}`);
  const index = db.users.findIndex(d => d.id === userId);
  if (index > -1) {
    db.users.splice(index, 1);
    return { success: true };
  }
  return { success: false, message: 'Dependent not found.' };
}

// GET /api/users?search=... (For adding new dependents)
export async function searchAllUsers(query) {
  await simulateDelay(400);
  console.log(`[Mock API] GET /api/users?search=${query}`);
  if (!query) return [];
  
  // Find users from the master list who are NOT already in the dependents list
  const currentDependentIds = db.users.map(d => d.id);
  
  return db.allSystemUsers.filter(user => {
    const isAlreadyDependent = currentDependentIds.includes(user.id);
    const matchesQuery = user.username.toLowerCase().includes(query.toLowerCase()) ||
                         `${user.firstName} ${user.lastName}`.toLowerCase().includes(query.toLowerCase());
    return !isAlreadyDependent && matchesQuery;
  });
}

// POST /api/dependents
export async function addDependent(userToAdd) {
  await simulateDelay();
  console.log(`[Mock API] POST /api/dependents`, userToAdd);
  const isAlreadyDependent = db.users.some(d => d.id === userToAdd.id);
  if (isAlreadyDependent) {
    return { success: false, message: 'User is already a dependent.' };
  }
  
  // In a real app, you'd create a CaregiverSeniorMap entry. Here, we just add to the list.
  const newDependent = {
    ...userToAdd,
    relation: 'N/A', // Default relation
    gender: 'male', // Default gender
  };
  db.users.push(newDependent);
  return { success: true, dependent: newDependent };
}

// GET /api/user/:userId
export async function getDependentDetails(userId) {
  await simulateDelay();
  console.log(`[Mock API] GET /api/user/${userId}`);
  const user = db.users.find(u => u.id === userId);
  if (!user) return null;
  // Return data similar to what the backend would send
  return {
    ...user,
    age: calculateAge(user.birthDate),
  };
}

// GET /api/user/:userId/medications
export async function getDependentMedications(userId) {
  await simulateDelay();
  console.log(`[Mock API] GET /api/user/${userId}/medications`);
  const maps = db.userMedMaps.filter(m => m.userId === userId);
  
  // Join with medicine data, like the backend would
  const populatedMeds = maps.map(map => {
    const medicine = db.medicines.find(m => m.id === map.medicineId);
    return {
      ...map,
      medicineTitle: medicine ? medicine.title : 'Unknown Medicine',
    };
  });
  return populatedMeds;
}

// DELETE /api/medication-map/:mapId
export async function deleteMedicationMapping(mapId) {
  await simulateDelay(300);
  console.log(`[Mock API] DELETE /api/medication-map/${mapId}`);
  const index = db.userMedMaps.findIndex(m => m.id === mapId);
  if (index > -1) {
    db.userMedMaps.splice(index, 1);
    return { success: true, message: 'Medication deleted.' };
  }
  return { success: false, message: 'Medication not found.' };
}

// GET /api/medicines?search=...
export async function searchMasterMedicineList(query) {
  await simulateDelay(400);
  console.log(`[Mock API] GET /api/medicines?search=${query}`);
  if (!query) return [];
  return db.medicines.filter(m => 
    m.title.toLowerCase().includes(query.toLowerCase())
  );
}

// POST /api/medicines
export async function createNewMasterMedicine(title, description = '') {
  await simulateDelay();
  console.log(`[Mock API] POST /api/medicines with title: ${title}`);
  const newMedicine = {
    id: Date.now(), // simple unique ID
    title,
    description,
  };
  db.medicines.push(newMedicine);
  return newMedicine;
}

// POST /api/user/:userId/medications
export async function addMedicationToDependent(userId, medMapData) {
  await simulateDelay();
  console.log(`[Mock API] POST /api/user/${userId}/medications`, medMapData);
  const newMap = {
    id: Date.now(),
    userId,
    ...medMapData,
  };
  db.userMedMaps.push(newMap);
  
  // Return the newly created resource, joined with medicine data
  const medicine = db.medicines.find(m => m.id === newMap.medicineId);
  return {
    ...newMap,
    medicineTitle: medicine ? medicine.title : 'Unknown Medicine',
  };
}

export async function addMedicineToMemory(title, description = '') {
  const newMed = {
    id: Date.now(),
    title,
    description
  };
  db.medicines.push(newMed);
  return newMed;
}

export async function getUpcomingMedicationsForCaregiver(caregiverId) {
  await simulateDelay();
  console.clear(); // Clear console for fresh debugging
  console.log(`[Mock API] ==> GET /upcoming-medications for caregiver: ${caregiverId}`);

  let current_hour = new Date().getHours();
  const today_iso = new Date().toISOString().split('T')[0];

  // --- TIME TRAVEL FOR TESTING ---
  // To guarantee you see the dinner medication, we force the time.
  current_hour = 19;
  // --- END TESTING BLOCK ---

  console.log(`[Mock API] Simulating current hour as: ${current_hour}`);

  let valid_slots = [];
  if (current_hour >= 4 && current_hour < 10) valid_slots = ['breakfast_before', 'breakfast_after'];
  else if (current_hour >= 10 && current_hour < 15) valid_slots = ['lunch_before', 'lunch_after'];
  else if (current_hour >= 16 && current_hour < 24) valid_slots = ['dinner_before', 'dinner_after'];

  if (valid_slots.length === 0) {
    console.log('[Mock API] No valid time slot for the current hour. Returning empty.');
    return { upcoming_medications: [] };
  }
  
  console.log(`[Mock API] Active time slots: [${valid_slots.join(', ')}]`);

  const senior_ids = db.caregiverDependentMap
    .filter(map => map.caregiverId === caregiverId)
    .map(map => map.dependentId);

  const final_results = [];

  // Loop through each dependent managed by the caregiver
  for (const seniorId of senior_ids) {
    // Get all valid meds for this specific dependent
    const all_meds_for_senior = db.userMedMaps.filter(med =>
      med.userId === seniorId &&
      med.start_date <= today_iso &&
      med.end_date >= today_iso
    );

    // <-- BUG FIX: The filtering logic is now moved directly inside the loop,
    // which is simpler and correctly matches the Python API's behavior.
    for (const med_map of all_meds_for_senior) {
      for (const slot of valid_slots) {
        if (med_map[slot]) { // Check if the property (e.g., 'dinner_after') is true
          const medicineInfo = db.medicines.find(m => m.id === med_map.medicineId);
          final_results.push({
            user_id: seniorId,
            medicine_id: med_map.medicineId,
            medicine_title: medicineInfo.title,
            dosage: med_map.dosage,
            start_date: med_map.start_date,
            end_date: med_map.end_date,
            // Format the slot name exactly like the Python API
            reminder_slot: slot.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
          });
        }
      }
    }
  }

  console.log('[Mock API] <== SUCCESS: Found medications:', final_results);
  return { upcoming_medications: final_results };
}


// Helper to get dependent details for the frontend component
export async function getDependentsDetails(dependentIds) {
    await simulateDelay(100);
    return db.users.filter(u => dependentIds.includes(u.id));
}

export async function getTodaysMedsForDependent(dependentId) {
    await simulateDelay(400);
    console.log(`[Mock API] GET all day medications for dependent: ${dependentId}`);

    // Define time slots with their associated hour for categorization
    const timeSlots = {
        breakfast_before: { hour: 8, label: '08:00 AM' },
        breakfast_after:  { hour: 9, label: '09:00 AM' },
        lunch_before:     { hour: 12, label: '12:00 PM' },
        lunch_after:      { hour: 13, label: '01:00 PM' },
        dinner_before:    { hour: 18, label: '06:00 PM' },
        dinner_after:     { hour: 19, label: '07:00 PM' },
    };

    const categorizedMeds = {
        daytime: [],
        nighttime: [],
    };
    
    const today_iso = new Date().toISOString().split('T')[0];
    
    // Get all med maps for this specific user
    const userMedMaps = db.userMedMaps.filter(med =>
        med.userId === dependentId &&
        med.start_date <= today_iso &&
        med.end_date >= today_iso
    );

    for (const medMap of userMedMaps) {
        for (const slotKey in timeSlots) {
            if (medMap[slotKey]) { // Check if e.g., medMap.breakfast_after is true
                const slotInfo = timeSlots[slotKey];
                const medicineInfo = db.medicines.find(m => m.id === medMap.medicineId);

                const medObject = {
                    id: `${medMap.id}-${slotKey}`, // Create a unique key for v-for
                    medicineName: medicineInfo.title,
                    dosage: medMap.dosage,
                    time: slotInfo.label,
                };

                // Categorize based on the hour (4 AM to 3:59 PM is daytime)
                if (slotInfo.hour >= 4 && slotInfo.hour < 16) {
                    categorizedMeds.daytime.push(medObject);
                } else {
                    categorizedMeds.nighttime.push(medObject);
                }
            }
        }
    }
    
    // Sort medications by time within each category
    const sortByTime = (a, b) => a.time.localeCompare(b.time);
    categorizedMeds.daytime.sort(sortByTime);
    categorizedMeds.nighttime.sort(sortByTime);

    console.log('[Mock API] Returning categorized meds:', categorizedMeds);
    return categorizedMeds;
}