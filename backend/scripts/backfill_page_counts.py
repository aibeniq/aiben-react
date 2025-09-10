#!/usr/bin/env python3
"""
Data backfill script to populate page counts for existing sources in the database.
This script should be run after the database migration to ensure all existing 
sources have accurate page counts.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend app directory to the Python path
backend_path = Path(__file__).parent / "backend" / "app"
sys.path.insert(0, str(backend_path))

from database import engine
from models import Source, KnowledgeBase
from services.page_counter import PageCounter
from services.knowledgebases import KnowledgeBaseService
from sqlmodel import Session, select

async def backfill_page_counts():
    """
    Backfill page counts for all existing sources that don't have them set.
    """
    page_counter = PageCounter()
    kb_service = KnowledgeBaseService()
    
    print("Starting page count backfill process...")
    
    with Session(engine) as session:
        # Find all sources where page_count is 0 (default value)
        statement = select(Source).where(Source.page_count == 0)
        sources_to_update = session.exec(statement).all()
        
        print(f"Found {len(sources_to_update)} sources to update")
        
        updated_sources = 0
        failed_sources = 0
        
        for source in sources_to_update:
            try:
                print(f"Processing source: {source.filename} (ID: {source.id})")
                
                # Get the file data - assuming it's stored in source.data
                if not source.data:
                    print(f"  Warning: No data found for source {source.id}, skipping")
                    continue
                
                # Count pages based on file extension
                page_count = page_counter.count_pages_from_bytes(
                    source.data, 
                    source.filename
                )
                
                # Update the source with the page count
                source.page_count = page_count
                session.add(source)
                
                print(f"  Updated source {source.id} with {page_count} pages")
                updated_sources += 1
                
            except Exception as e:
                print(f"  Error processing source {source.id}: {str(e)}")
                failed_sources += 1
                continue
        
        # Commit all source updates
        try:
            session.commit()
            print(f"\nCommitted {updated_sources} source updates")
        except Exception as e:
            print(f"Error committing source updates: {str(e)}")
            session.rollback()
            return
        
        # Now recalculate total_pages for all knowledge bases
        print("\nRecalculating total pages for all knowledge bases...")
        
        statement = select(KnowledgeBase)
        knowledge_bases = session.exec(statement).all()
        
        for kb in knowledge_bases:
            try:
                print(f"Updating knowledge base: {kb.name} (ID: {kb.id})")
                
                # Use the service method to recalculate total pages
                kb_service.recalculate_total_pages(session, kb.id)
                
                print(f"  Updated knowledge base {kb.id}")
                
            except Exception as e:
                print(f"  Error updating knowledge base {kb.id}: {str(e)}")
                continue
        
        # Commit knowledge base updates
        try:
            session.commit()
            print(f"\nCompleted knowledge base updates")
        except Exception as e:
            print(f"Error committing knowledge base updates: {str(e)}")
            session.rollback()
            return
    
    print(f"\nBackfill completed!")
    print(f"Sources updated: {updated_sources}")
    print(f"Sources failed: {failed_sources}")
    print(f"Knowledge bases updated: {len(knowledge_bases)}")

if __name__ == "__main__":
    print("Page Count Backfill Script")
    print("=" * 40)
    
    # Confirm before running
    response = input("This will update page counts for all existing sources. Continue? (y/N): ")
    if response.lower() != 'y':
        print("Backfill cancelled.")
        sys.exit(0)
    
    try:
        asyncio.run(backfill_page_counts())
    except KeyboardInterrupt:
        print("\nBackfill interrupted by user.")
    except Exception as e:
        print(f"Backfill failed with error: {str(e)}")
        sys.exit(1)
