#userauthcatr/models

from django.db import models
from django.contrib.postgres.fields import ArrayField
import pyotp

class Number_Otp(models.Model):
    otp_key = models.CharField(max_length=6 , default=pyotp.random_base32)
    def __str__(self):
        return self.otp_key
    
    def generate_opt(self):
        topt = pyotp.TOTP(self.otp_key , interval=300)
        return topt.now()
    
    def verify_opt(self , otp):
        topt = pyotp.TOTP(self , otp)
        topt = pyotp.TOTP(self.otp_key , interval=300)
        return topt.verify(otp)
        

