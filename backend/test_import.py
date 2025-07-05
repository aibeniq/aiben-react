#!/usr/bin/env python3

try:
    from app.api.routes.veradoc import router

    print("✅ Backend veradoc router import successful")
except Exception as e:
    print(f"❌ Backend import failed: {e}")

try:
    from app.models import RagChecklistRequest

    print("✅ RagChecklistRequest model import successful")
except Exception as e:
    print(f"❌ Model import failed: {e}")

try:
    from langchain_core.documents import Document

    print("✅ LangChain Document import successful")
except Exception as e:
    print(f"❌ LangChain import failed: {e}")

print("All imports tested!")
