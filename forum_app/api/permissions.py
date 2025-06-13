from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):

    # def has_object_permission(self, request, view, obj):
    #     if request.method in permissions.SAFE_METHODS:
    #         return True

    #     return obj.user == request.user or request.user.is_staff
    """
    Eigene Berechtigungsklasse, die nur den Besitzern eines Objekts oder Admins
    das Bearbeiten erlaubt. Sie ist flexibel und prüft, ob das Objekt ein 
    'user'-Attribut (wie bei Likes) oder ein 'author'-Attribut (wie bei Questions/Answers) hat.
    """
    def has_object_permission(self, request, view, obj):
        # Lese-Berechtigungen sind für jeden erlaubt.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Admins dürfen alles.
        if request.user.is_staff:
            return True

        # Prüfen, ob das Objekt ein 'user'-Attribut hat und ob es dem anfragenden Benutzer gehört.
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        # Prüfen, ob das Objekt ein 'author'-Attribut hat und ob es dem anfragenden Benutzer gehört.
        if hasattr(obj, 'author'):
            return obj.author == request.user
            
        return False


class CustomQuestionPermission(permissions.BasePermission):
    """
    Custom permission to allow:
    - Anyone to read (GET, HEAD, OPTIONS)
    - Authenticated users to create (POST)
    - Owners to update (PUT, PATCH)
    - Admins to delete (DELETE)
    """

    # def has_permission(self, request, view):
    #     if request.method in permissions.SAFE_METHODS:
    #         return True
    #     elif request.method == 'POST':
    #         return request.user.is_authenticated
    #     return False

    # def has_object_permission(self, request, view, obj):
    #     if request.method in permissions.SAFE_METHODS:
    #         return True
    #     elif request.method in ['PUT', 'PATCH']:
    #         return obj.author == request.user or request.user.is_staff
    #     elif request.method == 'DELETE':
    #         return request.user.is_staff
    #     return False
    """
    Eigene Berechtigungsklasse für das QuestionViewSet.
    - Jeder kann lesen (list/retrieve).
    - Authentifizierte Benutzer können erstellen (create).
    - Nur der Autor oder ein Admin kann aktualisieren/löschen (update/destroy).
    """
    def has_permission(self, request, view):
        # Für Aktionen, die keine spezifische Instanz betreffen (wie 'list' oder 'create'),
        # erlauben wir den Zugriff, wenn die Anfrage lesend ist oder wenn der Benutzer
        # für eine 'create'-Aktion authentifiziert ist.
        if view.action == 'list':
            return True
        elif view.action == 'create':
            return request.user.is_authenticated
        # Für Detail-Aktionen (retrieve, update, destroy) wird die Prüfung
        # an has_object_permission weitergegeben.
        elif view.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            return True
        else:
            return False

    def has_object_permission(self, request, view, obj):
        # Lese-Berechtigungen sind für jede Anfrage erlaubt.
        if view.action == 'retrieve':
            return True
        # Für Update/Destroy muss der Benutzer der Autor oder ein Admin sein.
        return obj.author == request.user or request.user.is_staff
