@receiver(post_save, sender=Doctor)
def create_token_tracker(sender, instance, created, **kwargs):
    if created:
        DoctorTokenTracker.objects.create(doctor=instance)