from django.db import models
from django.core.exceptions import ValidationError
from api.models import Hospital 
from datetime import timedelta
from django.utils import timezone


class Ward(models.Model):
   STATUS_CHOICES = [
       ('vacant', 'Vacant'),
       ('partially_occupied', 'Partially Occupied'),
       ('fully_occupied', 'Fully Occupied'), 
       ('maintenance', 'Maintenance')
   ]
   
   hospital = models.ForeignKey('api.Hospital', on_delete=models.CASCADE, to_field='hosp_ID')
   ward_name = models.CharField(max_length=100)
   no_of_beds = models.IntegerField(default=0)
   cost = models.DecimalField(max_digits=10, decimal_places=2)
   ward_img = models.CharField(max_length=255)
   ward_details = models.TextField()
   status = models.CharField(
       max_length=20,
       choices=STATUS_CHOICES, 
       default='vacant'
   )
   

   def save(self, *args, **kwargs):
    if self.pk is None:  # New ward creation
        current_beds = Ward.objects.filter(hospital_id=self.hospital_id)\
            .aggregate(total=models.Sum('no_of_beds'))['total'] or 0
        if current_beds + self.no_of_beds > self.hospital.hosp_no_of_beds:
            raise ValidationError("Exceeds hospital's total bed capacity")
        is_new = True
    else:  # Existing ward update
        old_ward = Ward.objects.get(pk=self.pk)
        is_new = False
        beds_to_add = self.no_of_beds - old_ward.no_of_beds
        
    super().save(*args, **kwargs)

    if is_new:  # Create all beds for new ward
        for bed_number in range(1, self.no_of_beds + 1):
            Bed.objects.create(
                ward=self,
                id=f"{self.pk}-B{bed_number:03}",
                status="vacant"
            )
    elif not is_new and beds_to_add > 0:  # Add new beds when count increases
        current_beds = self.beds.count()
        for bed_number in range(current_beds + 1, current_beds + beds_to_add + 1):
            Bed.objects.create(
                ward=self,
                id=f"{self.pk}-B{bed_number:03}",
                status="vacant"
            )

   def update_ward_status(self):
       beds = self.beds.all()
       if not beds:
           self.status = 'vacant'
       else:
           occupied_count = beds.filter(status='occupied').count()
           total_beds = beds.count()

           if occupied_count == 0:
               self.status = 'vacant'
           elif occupied_count == total_beds:
               self.status = 'fully_occupied'
           else:
               self.status = 'partially_occupied'

       self.save()

   def __str__(self):
       return f"{self.hospital.hosp_name} - {self.ward_name}"


class Bed(models.Model):
    STATUS_CHOICES = [
        ('vacant', 'Vacant'),
        ('occupied', 'Occupied'),
        ('maintenance', 'Maintenance')
    ]

    id = models.CharField(max_length=40, primary_key=True)  # Unique ID
    ward = models.ForeignKey(Ward, related_name='beds', on_delete=models.CASCADE)
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='vacant'
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Automatically update ward status after saving a bed
        self.ward.update_ward_status()

    def __str__(self):
        return f"{self.id} ({self.status}) in {self.ward.ward_name}"


class BedBooking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ]

    aadhar_number = models.CharField(max_length=12)
    prescription = models.FileField(upload_to='prescriptions/')
    booking_date = models.DateField()
    request_time = models.DateTimeField(auto_now_add=True)
    ward = models.ForeignKey('Ward', on_delete=models.CASCADE)
    hospital = models.ForeignKey('api.Hospital', on_delete=models.CASCADE)  # Updated reference
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Booking {self.id} - {self.user_mobile} - {self.status}"
    
    
class PatientAdmission(models.Model):
    patient_id = models.CharField(max_length=50, unique=True)
    patient_name = models.CharField(max_length=100)
    doctor_name = models.CharField(max_length=100)  # Changed from ForeignKey to CharField
    ward = models.ForeignKey(Ward, on_delete=models.CASCADE)
    bed = models.ForeignKey(Bed, on_delete=models.CASCADE)
    hospital = models.ForeignKey('api.Hospital', on_delete=models.CASCADE)
    admission_date = models.DateField()
    admission_letter = models.FileField(upload_to='admission_letters/')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='admitted')
    occupation_hours = models.IntegerField(default=24)  # New field
    release_time = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.patient_id:
            # Generate patient_id for new admission
            last_patient = PatientAdmission.objects.order_by('-patient_id').first()
            if last_patient and last_patient.patient_id.startswith('PAT'):
                last_number = int(last_patient.patient_id[3:])
                self.patient_id = f'PAT{str(last_number + 1).zfill(6)}'
            else:
                self.patient_id = 'PAT000001'

        if not self.pk:  # Only on creation
            self.bed.status = 'occupied'
            self.bed.save()
            self.release_time = timezone.now() + timedelta(hours=self.occupation_hours)
            
        super().save(*args, **kwargs)

def extend_time(self, additional_hours):
        self.occupation_hours += additional_hours
        self.release_time = self.release_time + timedelta(hours=additional_hours)
        self.save()

def __str__(self):
        return f"{self.patient_id} - {self.patient_name}"

class PatientDischarge(models.Model):
    discharge_id = models.AutoField(primary_key=True)
    admission = models.OneToOneField('PatientAdmission', on_delete=models.CASCADE)
    discharge_date = models.DateField()
    discharge_document = models.FileField(upload_to='discharge_documents/')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Discharge for {self.admission.patient_name}"
    
    class Meta:
        db_table = 'patient_discharge'
        
        
class DeathRecord(models.Model):
    patient_admission = models.OneToOneField(PatientAdmission, on_delete=models.CASCADE)
    death_date = models.DateField()
    death_certificate = models.FileField(upload_to='death_certificates/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Death Record for {self.patient_admission.patient_name}"

    class Meta:
        db_table = 'death_records'