import firebase_admin
from firebase_admin import credentials, firestore, auth, storage


cred = credentials.Certificate("serviceAccountKey.json")

# ✅ prevent duplicate initialization
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'clauseai1525.appspot.com'
    })

# ✅ export everything
db = firestore.client()
bucket = storage.bucket()