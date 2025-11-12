"""
One-time cleanup script for orphaned SourceData entries.

This script removes SourceData entries that are no longer referenced by any Source entries.
This can happen when knowledge bases are deleted but their SourceData entries remain.

Run this script once to clean up existing orphaned data, then the application-level
cleanup in the delete_knowledge_base endpoint will prevent future orphans.

Usage:
    python cleanup_orphaned_source_data.py
"""

from sqlmodel import Session, select
from app.core.db import engine
from app.models import Source, SourceData


def cleanup_orphaned_source_data():
    """Remove SourceData entries that have no associated Source entries."""
    print("🔍 Scanning for orphaned SourceData entries...")
    
    with Session(engine) as session:
        # Get all SourceData IDs that are still referenced by Source entries
        referenced_ids = set(
            session.exec(select(Source.source_data_id).distinct()).all()
        )
        
        print(f"📊 Found {len(referenced_ids)} SourceData entries still in use")
        
        # Get all SourceData entries
        all_source_data = session.exec(select(SourceData)).all()
        all_source_data_ids = {sd.id for sd in all_source_data}
        
        print(f"📊 Found {len(all_source_data_ids)} total SourceData entries")
        
        # Find orphaned entries (SourceData with no Source references)
        orphaned_ids = all_source_data_ids - referenced_ids
        
        if not orphaned_ids:
            print("✅ No orphaned SourceData entries found - database is clean!")
            return
        
        print(f"🗑️  Found {len(orphaned_ids)} orphaned SourceData entries to clean up")
        
        # Calculate total size being freed
        freed_bytes = 0
        for source_data_id in orphaned_ids:
            source_data = session.get(SourceData, source_data_id)
            if source_data:
                if source_data.data:
                    freed_bytes += len(source_data.data)
                session.delete(source_data)
        
        # Commit the deletions
        session.commit()
        
        print(f"\n✅ Successfully cleaned up {len(orphaned_ids)} orphaned SourceData entries")
        print(f"💾 Freed approximately {freed_bytes / (1024*1024):.2f} MB of storage")
        print(f"📉 Reduced SourceData table from {len(all_source_data_ids)} to {len(referenced_ids)} entries")


if __name__ == "__main__":
    print("=" * 60)
    print("Orphaned SourceData Cleanup Script")
    print("=" * 60)
    print()
    
    try:
        cleanup_orphaned_source_data()
        print()
        print("=" * 60)
        print("✅ Cleanup completed successfully!")
        print("=" * 60)
    except Exception as e:
        print()
        print("=" * 60)
        print(f"❌ Error during cleanup: {str(e)}")
        print("=" * 60)
        raise
