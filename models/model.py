from deepface import DeepFace

_facenet_model = None

def get_facenet_model():
    global _facenet_model
    if _facenet_model is None:
        _facenet_model = DeepFace.build_model("Facenet")
    return _facenet_model