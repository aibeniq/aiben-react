#!/usr/bin/env python3
"""
Database SSL Configuration Validator

This script validates the database SSL configuration and provides
recommendations based on the current environment.

Usage:
    python validate_db_ssl.py
    
    # Or in Docker:
    docker-compose run --rm backend python scripts/validate_db_ssl.py
"""

import os
import sys
from typing import Tuple

# Color codes for terminal output
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
RESET = "\033[0m"


def get_env(key: str, default: str = "") -> str:
    """Get environment variable value."""
    return os.getenv(key, default)


def check_ssl_configuration() -> Tuple[bool, list]:
    """
    Check SSL configuration and return (is_secure, recommendations).
    
    Returns:
        Tuple of (is_configuration_appropriate, list_of_recommendations)
    """
    recommendations = []
    
    environment = get_env("ENVIRONMENT", "local")
    postgres_server = get_env("POSTGRES_SERVER", "db")
    ssl_mode = get_env("POSTGRES_SSL_MODE", "prefer")
    
    print(f"\n{BLUE}=== Database SSL Configuration Validator ==={RESET}\n")
    print(f"Environment:     {environment}")
    print(f"Database Server: {postgres_server}")
    print(f"SSL Mode:        {ssl_mode}")
    print()
    
    # Detect local Docker environment
    is_local_docker = postgres_server in ["db", "localhost", "127.0.0.1", "postgres"]
    
    # Check 1: Local development
    if environment == "local":
        if is_local_docker:
            if ssl_mode in ["disable", "prefer"]:
                print(f"{GREEN}✅ Local Docker setup - SSL configuration appropriate{RESET}")
                print(f"   SSL will be disabled for performance (Docker internal network)")
            else:
                print(f"{YELLOW}⚠️  Local Docker with SSL enabled{RESET}")
                recommendations.append(
                    "Consider using POSTGRES_SSL_MODE=prefer or disable for local Docker to improve performance"
                )
        else:
            print(f"{YELLOW}⚠️  Local environment with external database{RESET}")
            if ssl_mode == "disable":
                recommendations.append(
                    "Using external database in local env - consider enabling SSL with POSTGRES_SSL_MODE=prefer"
                )
    
    # Check 2: Staging/Production
    elif environment in ["staging", "production"]:
        if is_local_docker:
            # Production with Docker on same instance
            if ssl_mode == "disable":
                print(f"{GREEN}✅ Production with same-instance Docker{RESET}")
                print(f"   SSL disabled is acceptable (connection never leaves the machine)")
            else:
                print(f"{BLUE}ℹ️  Production with same-instance Docker using SSL{RESET}")
                print(f"   This is secure but adds overhead. Consider POSTGRES_SSL_MODE=disable")
        else:
            # Production with external database
            if ssl_mode in ["require", "verify-ca", "verify-full"]:
                print(f"{GREEN}✅ Production with external database - SSL properly configured{RESET}")
                if ssl_mode == "verify-full":
                    print(f"   {GREEN}Excellent!{RESET} Using highest security level")
            elif ssl_mode == "prefer":
                print(f"{YELLOW}⚠️  Production with external database using 'prefer' mode{RESET}")
                recommendations.append(
                    "For production external databases, use POSTGRES_SSL_MODE=require or verify-full"
                )
            elif ssl_mode in ["disable", "allow"]:
                print(f"{RED}❌ SECURITY RISK: Production external database without SSL!{RESET}")
                recommendations.append(
                    "CRITICAL: Set POSTGRES_SSL_MODE=require for external production databases"
                )
                return False, recommendations
    
    # Check 3: SSL Mode validation
    valid_modes = ["disable", "allow", "prefer", "require", "verify-ca", "verify-full"]
    if ssl_mode not in valid_modes:
        print(f"{RED}❌ Invalid SSL mode: {ssl_mode}{RESET}")
        recommendations.append(
            f"Valid SSL modes: {', '.join(valid_modes)}"
        )
        return False, recommendations
    
    # Check 4: Certificate files (if using verify-ca or verify-full)
    if ssl_mode in ["verify-ca", "verify-full"]:
        cert_file = get_env("POSTGRES_SSLROOTCERT")
        if not cert_file:
            print(f"{YELLOW}⚠️  Using {ssl_mode} mode without certificate path{RESET}")
            recommendations.append(
                "Set POSTGRES_SSLROOTCERT environment variable to certificate file path"
            )
        elif not os.path.exists(cert_file):
            print(f"{RED}❌ Certificate file not found: {cert_file}{RESET}")
            recommendations.append(
                f"Certificate file {cert_file} does not exist"
            )
            return False, recommendations
        else:
            print(f"{GREEN}✅ Certificate file found: {cert_file}{RESET}")
    
    return True, recommendations


def print_recommendations(recommendations: list):
    """Print recommendations with formatting."""
    if recommendations:
        print(f"\n{YELLOW}=== Recommendations ==={RESET}\n")
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
    else:
        print(f"\n{GREEN}=== No Recommendations ==={RESET}")
        print("Your database SSL configuration looks good! 🎉")


def print_quick_fixes():
    """Print common quick fixes."""
    print(f"\n{BLUE}=== Quick Fixes ==={RESET}\n")
    print("For local Docker development:")
    print(f"  {GREEN}export POSTGRES_SSL_MODE=prefer{RESET}")
    print()
    print("For production (same-instance Docker):")
    print(f"  {GREEN}export POSTGRES_SSL_MODE=disable{RESET}")
    print()
    print("For production (external database like RDS):")
    print(f"  {GREEN}export POSTGRES_SSL_MODE=require{RESET}")
    print()
    print("For maximum security with certificates:")
    print(f"  {GREEN}export POSTGRES_SSL_MODE=verify-full{RESET}")
    print(f"  {GREEN}export POSTGRES_SSLROOTCERT=/path/to/ca-bundle.pem{RESET}")


def test_connection():
    """Test database connection with current settings."""
    print(f"\n{BLUE}=== Testing Database Connection ==={RESET}\n")
    
    try:
        from app.core.config import Settings
        from app.core.db import engine
        
        settings = Settings()
        
        print(f"Connecting to database...")
        print(f"Connection string: {str(settings.SQLALCHEMY_DATABASE_URI)[:60]}...")
        
        with engine.connect() as conn:
            # Check SSL status
            result = conn.execute(
                "SELECT ssl, version, cipher FROM pg_stat_ssl WHERE pid = pg_backend_pid()"
            )
            row = result.fetchone()
            
            if row:
                ssl_enabled, ssl_version, cipher = row
                if ssl_enabled:
                    print(f"{GREEN}✅ SSL is ACTIVE{RESET}")
                    print(f"   Version: {ssl_version}")
                    print(f"   Cipher:  {cipher}")
                else:
                    print(f"{YELLOW}ℹ️  SSL is NOT active{RESET}")
                    print(f"   This is expected for local Docker environments")
            else:
                print(f"{YELLOW}⚠️  Could not determine SSL status{RESET}")
            
            print(f"\n{GREEN}✅ Database connection successful!{RESET}")
            return True
            
    except ImportError:
        print(f"{YELLOW}⚠️  Cannot test connection (app modules not available){RESET}")
        print(f"   Run this script inside the backend container:")
        print(f"   docker-compose run --rm backend python scripts/validate_db_ssl.py")
        return None
    except Exception as e:
        print(f"{RED}❌ Database connection failed:{RESET}")
        print(f"   {str(e)}")
        return False


def main():
    """Main validation routine."""
    print()
    
    # Check configuration
    is_secure, recommendations = check_ssl_configuration()
    
    # Print recommendations
    print_recommendations(recommendations)
    
    # Test connection if possible
    connection_ok = test_connection()
    
    # Print quick fixes
    if recommendations or connection_ok is False:
        print_quick_fixes()
    
    # Print documentation reference
    print(f"\n{BLUE}=== Documentation ==={RESET}\n")
    print("📖 Full guide: DATABASE_ENCRYPTION_SETUP.md")
    print("📋 Quick ref:  DATABASE_ENCRYPTION_QUICKREF.md")
    
    # Exit code
    print()
    if is_secure and (connection_ok is None or connection_ok):
        print(f"{GREEN}✅ Validation complete - configuration looks good!{RESET}\n")
        sys.exit(0)
    else:
        print(f"{RED}❌ Validation found issues - please review recommendations{RESET}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
