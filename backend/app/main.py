from fastapi import FastAPI
app = FastAPI(title='PREPPER MAP API', version='2.5.0')
@app.get('/health')
def health(): return {'status':'ok','version':'2.5.0'}
