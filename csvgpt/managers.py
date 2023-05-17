from django.db import models

class ActivityQuerySet(models.QuerySet):
    def isActive(self):
        return self.filter(active=True)
    
    def isInActive(self):
        return self.filter(active=False)

    def isDeleted(self):
        return self.filter(is_deleted=True)
    
    def isNotDeleted(self):
        return self.filter(is_deleted=False)
    
    def isActiveDeleted(self):
        return self.filter(active=True, is_deleted=True)
    
    def isActiveNotDeleted(self):
        return self.filter(active=True, is_deleted=False)

    def isNotActiveDeleted(self):
        return self.filter(active=False, is_deleted=True)