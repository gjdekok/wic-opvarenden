class OpvarendenRouter:
    """
    A router to control all database operations on models in the opvarenden app.
    """

    def db_for_read(self, model, **hints):
        """
        Direct all read operations on opvarenden models to the opvarenden database.
        """
        if model._meta.app_label == 'opvarenden':
            return 'opvarenden'
        return 'default'

    def db_for_write(self, model, **hints):
        """
        Prevent write operations on opvarenden models.
        """
        if model._meta.app_label == 'opvarenden':
            return None  # Returning None means no write database is configured.
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the opvarenden app is involved.
        """
        if obj1._meta.app_label == 'opvarenden' or obj2._meta.app_label == 'opvarenden':
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Prevent migrations for the opvarenden app.
        """
        if app_label == 'opvarenden':
            return False
        return None
