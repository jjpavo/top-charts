class TopChartsDBRouter(object):
    """
    A router to control Top Charts db operations
    """

    def db_for_read(self, model, **hints):
        "Point all operations on top_charts models to 'db_top_charts'"
        from django.conf import settings
        if 'db_top_charts' not in settings.DATABASES:
            return None
        if model._meta.app_label == 'app1':
            return 'db_top_charts'
        return None

    def db_for_write(self, model, **hints):
        "Point all operations on app1 models to 'db_top_charts'"
        from django.conf import settings
        if 'db_top_charts' not in settings.DATABASES:
            return None
        if model._meta.app_label == 'top_charts':
            return 'db_top_charts'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        "Allow any relation if a model in top_charts is involved"
        from django.conf import settings
        if 'db_top_charts' not in settings.DATABASES:
            return None
        if obj1._meta.app_label == 'top_charts' or obj2._meta.app_label == 'top_charts':
            return True
        return None

    def allow_syncdb(self, db, model):
        "Make sure the app1 app only appears on the 'top_charts' db"
        from django.conf import settings
        if 'db_top_charts' not in settings.DATABASES:
            return None
        if db == 'db_top_charts':
            return model._meta.app_label == 'top_charts'
        elif model._meta.app_label == 'top_charts':
            return False
        return None
