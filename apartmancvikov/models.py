from django.db import models


class Booking(models.Model):
    start = models.DateField()
    end = models.DateField()
    uid = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f"{self.start} - {self.end}: {self.uid}"
