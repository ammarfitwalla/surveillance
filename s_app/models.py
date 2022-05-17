from django.db import models
from PIL import Image


class Employee(models.Model):
    # emp_id = models.CharField(max_length=255, unique=True, error_messages={
    #     "unique": "The Employee ID you entered already exist."
    # })
    emp_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    age = models.IntegerField()
    gender = models.CharField(max_length=255)
    mobile = models.CharField(max_length=20, null=True)
    designation = models.CharField(max_length=255)
    shift = models.CharField(max_length=255)
    train = models.BooleanField(default=False)

    def __str__(self):
        return str(self.emp_id)


class EmployeeImage(models.Model):
    model = models.ForeignKey(Employee, on_delete=models.CASCADE)
    image = models.ImageField()

    def save(self, *args, **kwargs):
        super(EmployeeImage, self).save(*args, **kwargs)

        img = Image.open(self.image.path)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)

    def __str__(self):
        return str(self.model.emp_id) + '_' + str(self.model.name)


class Attendance(models.Model):
    name = models.CharField(max_length=255)
    image = models.CharField(max_length=255, null=True)
    emp_id = models.CharField(max_length=255)
    designation = models.CharField(max_length=255)
    shift = models.CharField(max_length=255)
    enter = models.DateTimeField(null=True, blank=True)
    exit = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.name)


class UnidentifiedFaces(models.Model):
    image = models.CharField(max_length=255)
    enter = models.DateTimeField(null=True, blank=True)
