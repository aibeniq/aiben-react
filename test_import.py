import traceback

try:
    from app.api.routes.reportgenie import router

    print("Import successful")
    print(f"Router has {len(router.routes)} routes")
    for route in router.routes:
        print(f"  {route.methods} {route.path}")
except Exception as e:
    print(f"Import failed: {e}")
    traceback.print_exc()
