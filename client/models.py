from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

class Client(models.Model):
    user = models.OneToOneField("delivery.User", on_delete=models.CASCADE)


# NOTE: Unused
class Voucher(models.Model):
    PERCENTAGE_DEDUCTION = "PD"
    FIXED_DEDUCTION = "FD"
    DELIVERY_DEDUCTION = "DD"
    VOUCHER_TYPES = [
        (PERCENTAGE_DEDUCTION, "Percentage deduction on food cost (excluding delivery)"), 
        (FIXED_DEDUCTION, "Fixed deduction on food cost (excluding delivery)"), 
        (DELIVERY_DEDUCTION, "Fixed deduction on delivery cost")
    ]
    type = models.CharField(choices=VOUCHER_TYPES, max_length=2)

    deduction = models.FloatField(default=0)
    # TODO: do class-level validation for deduction w.r.t each voucher type
    
    def is_eligible(self, order):
        '''
        Must override this method when implementing new voucher
        '''
        raise ValidationError("Must implement is_eligible() before saving Voucher!")


class Review(models.Model):
    client = models.ForeignKey("client.Client", on_delete=models.CASCADE, related_name='reviews')
    restaurant = models.ForeignKey("merchant.Restaurant", on_delete=models.CASCADE, related_name='reviews')
    text = models.CharField(max_length=2000)
    created = models.DateTimeField(default=timezone.now)
    
    class Ratings(models.IntegerChoices):
        ONE = 1
        TWO = 2
        THREE = 3
        FOUR = 4
        FIVE = 5

    rating = models.PositiveSmallIntegerField(choices=Ratings.choices)
