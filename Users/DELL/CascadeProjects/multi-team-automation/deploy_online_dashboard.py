#!/usr/bin/env python3
"""
MFM Corporation - Online Dashboard Deployment Script
Deploys the automation dashboard to cloud hosting with remote access
"""

import os
import sys
import asyncio
import logging
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
import tempfile
import shutil

# Add src to path
sys.path.append('src')
sys.path.append('.')

from src.config_validator import ConfigValidator, validate_environment
from src.supabase_client import get_supabase_manager
from src.exceptions import MFMException, SystemException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OnlineDashboardDeployment:
    """Complete online dashboard deployment solution"""
    
    def __init__(self):
        self.deployment_options = {
            "render": {
                "name": "Render",
                "type": "paas",
                "free_tier": True,
                "custom_domain": True,
                "database": "postgresql",
                "deployment": "git_based"
            },
            "railway": {
                "name": "Railway",
                "type": "paas",
                "free_tier": True,
                "custom_domain": True,
                "database": "postgresql",
                "deployment": "git_based"
            },
            "heroku": {
                "name": "Heroku",
                "type": "paas",
                "free_tier": False,
                "custom_domain": True,
                "database": "postgresql",
                "deployment": "git_based"
            },
            "vercel": {
                "name": "Vercel",
                "type": "frontend",
                "free_tier": True,
                "custom_domain": True,
                "database": "external",
                "deployment": "git_based"
            },
            "netlify": {
                "name": "Netlify",
                "type": "frontend",
                "free_tier": True,
                "custom_domain": True,
                "database": "external",
                "deployment": "git_based"
            },
            "digitalocean": {
                "name": "DigitalOcean",
                "type": "vps",
                "free_tier": False,
                "custom_domain": True,
                "database": "postgresql",
                "deployment": "manual"
            }
        }
        
    async def deploy_dashboard(self, platform: str = "render", custom_domain: Optional[str] = None) -> Dict[str, Any]:
        """Deploy dashboard to specified platform"""
        logger.info(f"🚀 Deploying MFM Corporation Dashboard to {platform}")
        
        try:
            # Validate platform
            if platform not in self.deployment_options:
                return {"success": False, "error": f"Unsupported platform: {platform}"}
            
            platform_info = self.deployment_options[platform]
            
            # Prepare deployment
            prep_result = await self._prepare_deployment(platform, custom_domain)
            if not prep_result["success"]:
                return prep_result
            
            # Deploy based on platform
            if platform in ["render", "railway", "heroku"]:
                return await self._deploy_paas(platform, platform_info, custom_domain)
            elif platform in ["vercel", "netlify"]:
                return await self._deploy_frontend(platform, platform_info, custom_domain)
            elif platform == "digitalocean":
                return await self._deploy_vps(platform, platform_info, custom_domain)
            else:
                return {"success": False, "error": f"Deployment not implemented for {platform}"}
                
        except Exception as e:
            logger.error(f"❌ Deployment failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _prepare_deployment(self, platform: str, custom_domain: Optional[str]) -> Dict[str, Any]:
        """Prepare for deployment"""
        try:
            logger.info("📋 Preparing deployment configuration")
            
            # Validate environment
            validation_results = validate_environment()
            if not validation_results["valid"]:
                return {"success": False, "error": "Environment validation failed", "details": validation_results["errors"]}
            
            # Test database connection
            try:
                supabase_manager = await get_supabase_manager()
                if not await supabase_manager.test_connection():
                    return {"success": False, "error": "Database connection failed"}
            except Exception as e:
                return {"success": False, "error": f"Database test failed: {str(e)}"}
            
            # Create deployment files
            await self._create_deployment_files(platform, custom_domain)
            
            return {"success": True, "message": "Deployment preparation completed"}
            
        except Exception as e:
            return {"success": False, "error": f"Preparation failed: {str(e)}"}
    
    async def _create_deployment_files(self, platform: str, custom_domain: Optional[str]):
        """Create platform-specific deployment files"""
        
        if platform == "render":
            await self._create_render_files()
        elif platform == "railway":
            await self._create_railway_files()
        elif platform == "heroku":
            await self._create_heroku_files()
        elif platform == "vercel":
            await self._create_vercel_files()
        elif platform == "netlify":
            await self._create_netlify_files()
        elif platform == "digitalocean":
            await self._create_digitalocean_files()
    
    async def _create_render_files(self):
        """Create Render deployment files"""
        
        # render.yaml
        render_config = {
            "services": [
                {
                    "type": "web",
                    "name": "mfm-dashboard",
                    "env": "python",
                    "plan": "free",
                    "buildCommand": "pip install -r requirements.txt",
                    "startCommand": "python dashboard_server.py",
                    "healthCheckPath": "/health",
                    "envVars": [
                        {"key": "PYTHON_VERSION", "value": "3.9"},
                        {"key": "SUPABASE_URL", "sync": False},
                        {"key": "SUPABASE_KEY", "sync": False},
                        {"key": "JWT_SECRET_KEY", "sync": False, "generateValue": "true"},
                        {"key": "ENVIRONMENT", "value": "production"}
                    ]
                }
            ]
        }
        
        with open("render.yaml", "w") as f:
            import yaml
            yaml.dump(render_config, f, default_flow_style=False)
        
        logger.info("✅ Created render.yaml")
    
    async def _create_railway_files(self):
        """Create Railway deployment files"""
        
        # railway.json
        railway_config = {
            "build": {
                "builder": "NIXPACKS"
            },
            "deploy": {
                "startCommand": "python dashboard_server.py",
                "healthcheckPath": "/health"
            }
        }
        
        with open("railway.json", "w") as f:
            json.dump(railway_config, f, indent=2)
        
        # nixpacks.toml
        nixpacks_config = """
[phases.setup]
nixPkgs = ["python39", "postgresql"]

[phases.build]
cmds = ["pip install -r requirements.txt"]

[phases.start]
cmd = "python dashboard_server.py"
"""
        
        with open("nixpacks.toml", "w") as f:
            f.write(nixpacks_config.strip())
        
        logger.info("✅ Created Railway deployment files")
    
    async def _create_heroku_files(self):
        """Create Heroku deployment files"""
        
        # Procfile
        procfile = "web: python dashboard_server.py"
        with open("Procfile", "w") as f:
            f.write(procfile)
        
        # runtime.txt
        runtime = "python-3.9.16"
        with open("runtime.txt", "w") as f:
            f.write(runtime)
        
        logger.info("✅ Created Heroku deployment files")
    
    async def _create_vercel_files(self):
        """Create Vercel deployment files"""
        
        # vercel.json
        vercel_config = {
            "version": 2,
            "builds": [
                {
                    "src": "dashboard_server.py",
                    "use": "@vercel/python"
                }
            ],
            "routes": [
                {
                    "src": "/(.*)",
                    "dest": "/dashboard_server.py"
                }
            ],
            "env": {
                "SUPABASE_URL": "@supabase_url",
                "SUPABASE_KEY": "@supabase_key",
                "JWT_SECRET_KEY": "@jwt_secret"
            }
        }
        
        with open("vercel.json", "w") as f:
            json.dump(vercel_config, f, indent=2)
        
        logger.info("✅ Created Vercel deployment files")
    
    async def _create_netlify_files(self):
        """Create Netlify deployment files"""
        
        # netlify.toml
        netlify_config = """
[build]
  command = "echo 'Netlify build complete'"

[functions]
  directory = "netlify/functions"

[environment]
  PYTHON_VERSION = "3.9"
"""
        
        with open("netlify.toml", "w") as f:
            f.write(netlify_config.strip())
        
        # Create functions directory
        Path("netlify/functions").mkdir(parents=True, exist_ok=True)
        
        logger.info("✅ Created Netlify deployment files")
    
    async def _create_digitalocean_files(self):
        """Create DigitalOcean deployment files"""
        
        # docker-compose.yml
        docker_compose = """
version: '3.8'

services:
  dashboard:
    build: .
    ports:
      - "8000:8000"
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - ENVIRONMENT=production
    depends_on:
      - db
    restart: unless-stopped

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=mfm_automation
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
"""
        
        with open("docker-compose.yml", "w") as f:
            f.write(docker_compose.strip())
        
        # Dockerfile
        dockerfile = """
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "dashboard_server.py"]
"""
        
        with open("Dockerfile", "w") as f:
            f.write(dockerfile.strip())
        
        logger.info("✅ Created DigitalOcean deployment files")
    
    async def _deploy_paas(self, platform: str, platform_info: Dict[str, Any], custom_domain: Optional[str]) -> Dict[str, Any]:
        """Deploy to PaaS platform"""
        
        if platform == "render":
            return await self._deploy_to_render(platform_info, custom_domain)
        elif platform == "railway":
            return await self._deploy_to_railway(platform_info, custom_domain)
        elif platform == "heroku":
            return await self._deploy_to_heroku(platform_info, custom_domain)
        else:
            return {"success": False, "error": f"PaaS deployment not implemented for {platform}"}
    
    async def _deploy_to_render(self, platform_info: Dict[str, Any], custom_domain: Optional[str]) -> Dict[str, Any]:
        """Deploy to Render"""
        try:
            logger.info("🚀 Deploying to Render")
            
            instructions = """
🎯 RENDER DEPLOYMENT INSTRUCTIONS:

1. CREATE RENDER ACCOUNT:
   - Go to https://render.com
   - Sign up for a free account
   - Connect your GitHub repository

2. DEPLOYMENT STEPS:
   - Push your code to GitHub
   - In Render, click "New" → "Web Service"
   - Connect your GitHub repository
   - Render will automatically detect render.yaml
   - Configure environment variables:
     * SUPABASE_URL: Your Supabase URL
     * SUPABASE_KEY: Your Supabase anon key
     * JWT_SECRET_KEY: Generate a secure secret

3. CUSTOM DOMAIN (Optional):
   - In Render service settings, add custom domain
   - Update DNS records as instructed

4. DEPLOYMENT:
   - Click "Create Web Service"
   - Render will automatically build and deploy
   - Your dashboard will be available at: https://your-app-name.onrender.com

📋 AFTER DEPLOYMENT:
- Test your dashboard at the provided URL
- Monitor deployment logs in Render dashboard
- Set up custom domain if desired
"""
            
            return {
                "success": True,
                "platform": "Render",
                "instructions": instructions.strip(),
                "next_steps": [
                    "Create Render account at https://render.com",
                    "Connect GitHub repository",
                    "Configure environment variables",
                    "Deploy and test dashboard"
                ]
            }
            
        except Exception as e:
            return {"success": False, "error": f"Render deployment failed: {str(e)}"}
    
    async def _deploy_to_railway(self, platform_info: Dict[str, Any], custom_domain: Optional[str]) -> Dict[str, Any]:
        """Deploy to Railway"""
        try:
            logger.info("🚀 Deploying to Railway")
            
            instructions = """
🎯 RAILWAY DEPLOYMENT INSTRUCTIONS:

1. CREATE RAILWAY ACCOUNT:
   - Go to https://railway.app
   - Sign up for a free account
   - Install Railway CLI: npm install -g @railway/cli

2. DEPLOYMENT STEPS:
   - Login: railway login
   - Initialize project: railway init
   - Add environment variables:
     railway variables set SUPABASE_URL=your_supabase_url
     railway variables set SUPABASE_KEY=your_supabase_key
     railway variables set JWT_SECRET_KEY=your_secret_key
   - Deploy: railway up

3. CUSTOM DOMAIN (Optional):
   - In Railway project settings, add custom domain
   - Update DNS records as instructed

4. DEPLOYMENT:
   - Railway will automatically build and deploy
   - Your dashboard will be available at: https://your-app-name.railway.app

📋 AFTER DEPLOYMENT:
- Test your dashboard at the provided URL
- Monitor deployment logs in Railway dashboard
- Set up custom domain if desired
"""
            
            return {
                "success": True,
                "platform": "Railway",
                "instructions": instructions.strip(),
                "next_steps": [
                    "Create Railway account at https://railway.app",
                    "Install Railway CLI",
                    "Initialize project and deploy",
                    "Configure environment variables"
                ]
            }
            
        except Exception as e:
            return {"success": False, "error": f"Railway deployment failed: {str(e)}"}
    
    async def _deploy_to_heroku(self, platform_info: Dict[str, Any], custom_domain: Optional[str]) -> Dict[str, Any]:
        """Deploy to Heroku"""
        try:
            logger.info("🚀 Deploying to Heroku")
            
            instructions = """
🎯 HEROKU DEPLOYMENT INSTRUCTIONS:

1. CREATE HEROKU ACCOUNT:
   - Go to https://heroku.com
   - Sign up for an account (paid tier required for Python apps)
   - Install Heroku CLI

2. DEPLOYMENT STEPS:
   - Login: heroku login
   - Create app: heroku create your-app-name
   - Add PostgreSQL: heroku addons:create heroku-postgresql:hobby-dev
   - Set environment variables:
     heroku config:set SUPABASE_URL=your_supabase_url
     heroku config:set SUPABASE_KEY=your_supabase_key
     heroku config:set JWT_SECRET_KEY=your_secret_key
   - Deploy: git push heroku main

3. CUSTOM DOMAIN (Optional):
   - Add custom domain: heroku domains:add yourdomain.com
   - Update DNS records as instructed

4. DEPLOYMENT:
   - Heroku will automatically build and deploy
   - Your dashboard will be available at: https://your-app-name.herokuapp.com

📋 AFTER DEPLOYMENT:
- Test your dashboard at the provided URL
- Monitor deployment logs: heroku logs --tail
- Set up custom domain if desired
"""
            
            return {
                "success": True,
                "platform": "Heroku",
                "instructions": instructions.strip(),
                "next_steps": [
                    "Create Heroku account",
                    "Install Heroku CLI",
                    "Create app and configure",
                    "Deploy using git push"
                ]
            }
            
        except Exception as e:
            return {"success": False, "error": f"Heroku deployment failed: {str(e)}"}
    
    async def _deploy_frontend(self, platform: str, platform_info: Dict[str, Any], custom_domain: Optional[str]) -> Dict[str, Any]:
        """Deploy to frontend platform"""
        
        if platform == "vercel":
            return await self._deploy_to_vercel(platform_info, custom_domain)
        elif platform == "netlify":
            return await self._deploy_to_netlify(platform_info, custom_domain)
        else:
            return {"success": False, "error": f"Frontend deployment not implemented for {platform}"}
    
    async def _deploy_to_vercel(self, platform_info: Dict[str, Any], custom_domain: Optional[str]) -> Dict[str, Any]:
        """Deploy to Vercel"""
        try:
            logger.info("🚀 Deploying to Vercel")
            
            instructions = """
🎯 VERCEL DEPLOYMENT INSTRUCTIONS:

1. CREATE VERCEL ACCOUNT:
   - Go to https://vercel.com
   - Sign up for a free account
   - Install Vercel CLI: npm install -g vercel

2. DEPLOYMENT STEPS:
   - Login: vercel login
   - Deploy: vercel
   - Configure environment variables in Vercel dashboard:
     * SUPABASE_URL: Your Supabase URL
     * SUPABASE_KEY: Your Supabase anon key
     * JWT_SECRET_KEY: Your secret key

3. CUSTOM DOMAIN (Optional):
   - In Vercel project settings, add custom domain
   - Update DNS records as instructed

4. DEPLOYMENT:
   - Vercel will automatically build and deploy
   - Your dashboard will be available at: https://your-app-name.vercel.app

📋 AFTER DEPLOYMENT:
- Test your dashboard at the provided URL
- Monitor deployment logs in Vercel dashboard
- Set up custom domain if desired
"""
            
            return {
                "success": True,
                "platform": "Vercel",
                "instructions": instructions.strip(),
                "next_steps": [
                    "Create Vercel account at https://vercel.com",
                    "Install Vercel CLI",
                    "Deploy using vercel command",
                    "Configure environment variables"
                ]
            }
            
        except Exception as e:
            return {"success": False, "error": f"Vercel deployment failed: {str(e)}"}
    
    async def _deploy_to_netlify(self, platform_info: Dict[str, Any], custom_domain: Optional[str]) -> Dict[str, Any]:
        """Deploy to Netlify"""
        try:
            logger.info("🚀 Deploying to Netlify")
            
            instructions = """
🎯 NETLIFY DEPLOYMENT INSTRUCTIONS:

1. CREATE NETLIFY ACCOUNT:
   - Go to https://netlify.com
   - Sign up for a free account
   - Install Netlify CLI: npm install -g netlify-cli

2. DEPLOYMENT STEPS:
   - Login: netlify login
   - Initialize: netlify init
   - Deploy: netlify deploy --prod
   - Configure environment variables in Netlify dashboard:
     * SUPABASE_URL: Your Supabase URL
     * SUPABASE_KEY: Your Supabase anon key
     * JWT_SECRET_KEY: Your secret key

3. CUSTOM DOMAIN (Optional):
   - In Netlify site settings, add custom domain
   - Update DNS records as instructed

4. DEPLOYMENT:
   - Netlify will automatically deploy
   - Your dashboard will be available at: https://your-app-name.netlify.app

📋 AFTER DEPLOYMENT:
- Test your dashboard at the provided URL
- Monitor deployment logs in Netlify dashboard
- Set up custom domain if desired
"""
            
            return {
                "success": True,
                "platform": "Netlify",
                "instructions": instructions.strip(),
                "next_steps": [
                    "Create Netlify account at https://netlify.com",
                    "Install Netlify CLI",
                    "Initialize and deploy",
                    "Configure environment variables"
                ]
            }
            
        except Exception as e:
            return {"success": False, "error": f"Netlify deployment failed: {str(e)}"}
    
    async def _deploy_vps(self, platform: str, platform_info: Dict[str, Any], custom_domain: Optional[str]) -> Dict[str, Any]:
        """Deploy to VPS platform"""
        
        if platform == "digitalocean":
            return await self._deploy_to_digitalocean(platform_info, custom_domain)
        else:
            return {"success": False, "error": f"VPS deployment not implemented for {platform}"}
    
    async def _deploy_to_digitalocean(self, platform_info: Dict[str, Any], custom_domain: Optional[str]) -> Dict[str, Any]:
        """Deploy to DigitalOcean"""
        try:
            logger.info("🚀 Deploying to DigitalOcean")
            
            instructions = """
🎯 DIGITALOCEAN DEPLOYMENT INSTRUCTIONS:

1. CREATE DIGITALOCEAN DROPLET:
   - Go to https://digitalocean.com
   - Create a new Droplet (Ubuntu 20.04 recommended)
   - Choose appropriate size ($6/month minimum)
   - Add SSH key for secure access

2. SERVER SETUP:
   - SSH into your Droplet
   - Install Docker: curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh
   - Install Docker Compose: sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   - Make executable: sudo chmod +x /usr/local/bin/docker-compose

3. DEPLOYMENT:
   - Copy your project files to the server
   - Create .env file with your environment variables
   - Run: docker-compose up -d

4. CUSTOM DOMAIN (Optional):
   - Point your domain to the Droplet IP
   - Configure Nginx for SSL and reverse proxy

5. DEPLOYMENT:
   - Your dashboard will be available at: http://your-droplet-ip:8000
   - For production, set up Nginx and SSL

📋 AFTER DEPLOYMENT:
- Test your dashboard at the provided URL
- Monitor container logs: docker-compose logs -f
- Set up SSL certificate with Let's Encrypt
"""
            
            return {
                "success": True,
                "platform": "DigitalOcean",
                "instructions": instructions.strip(),
                "next_steps": [
                    "Create DigitalOcean Droplet",
                    "Install Docker and Docker Compose",
                    "Deploy using docker-compose",
                    "Set up SSL and custom domain"
                ]
            }
            
        except Exception as e:
            return {"success": False, "error": f"DigitalOcean deployment failed: {str(e)}"}
    
    async def get_platform_recommendations(self) -> Dict[str, Any]:
        """Get platform recommendations based on needs"""
        
        recommendations = {
            "free_best": {
                "platform": "render",
                "reason": "Free tier, easy setup, Python support, custom domains",
                "url": "https://render.com"
            },
            "easiest": {
                "platform": "vercel", 
                "reason": "Simplest deployment, excellent UI, free tier",
                "url": "https://vercel.com"
            },
            "most_powerful": {
                "platform": "digitalocean",
                "reason": "Full server control, best performance, scalable",
                "url": "https://digitalocean.com"
            },
            "developer_friendly": {
                "platform": "railway",
                "reason": "Great CLI, modern interface, good for developers",
                "url": "https://railway.app"
            }
        }
        
        return recommendations
    
    async def create_deployment_guide(self, platform: str) -> str:
        """Create comprehensive deployment guide"""
        
        guide = f"""
# MFM Corporation Dashboard - {platform.title()} Deployment Guide

## 🚀 Quick Start

### 1. Prerequisites
- Active {platform.title()} account
- GitHub repository with your code
- Supabase project configured
- Environment variables ready

### 2. Environment Variables Required
```
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
JWT_SECRET_KEY=your_super_secret_jwt_key
ENVIRONMENT=production
```

### 3. Deployment Steps

#### Step 1: Prepare Your Code
```bash
# Ensure all files are committed
git add .
git commit -m "Ready for {platform.title()} deployment"
git push origin main
```

#### Step 2: Connect to {platform.title()}
- Visit {self.deployment_options[platform]['url']}
- Sign up/login to your account
- Connect your GitHub repository

#### Step 3: Configure Deployment
- {platform.title()} will detect your project type
- Configure build settings if needed
- Add environment variables in dashboard

#### Step 4: Deploy
- Click deploy button
- Wait for build to complete
- Test your dashboard at provided URL

### 4. Post-Deployment Checklist
- [ ] Dashboard loads correctly
- [ ] All teams are accessible
- [ ] Real-time updates work
- [ ] Authentication functions
- [ ] Database connectivity verified
- [ ] Custom domain configured (if needed)

### 5. Monitoring and Maintenance
- Monitor deployment logs
- Check system health regularly
- Update dependencies as needed
- Backup your data

## 🔧 Troubleshooting

### Common Issues
1. **Build Failures**: Check requirements.txt and Python version
2. **Database Connection**: Verify Supabase credentials
3. **Environment Variables**: Ensure all required vars are set
4. **Port Issues**: Check if port 8000 is accessible

### Support Resources
- {platform.title()} Documentation
- MFM Corporation System Docs
- Community Support Forums

## 📞 Getting Help

If you encounter issues:
1. Check deployment logs
2. Verify environment configuration
3. Test locally first
4. Contact support if needed

---

**Happy Monitoring! 🎯**
"""
        
        return guide.strip()

async def main():
    """Main deployment function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Deploy MFM Corporation Dashboard Online")
    parser.add_argument("--platform", choices=["render", "railway", "heroku", "vercel", "netlify", "digitalocean"], 
                       default="render", help="Deployment platform")
    parser.add_argument("--domain", help="Custom domain (optional)")
    parser.add_argument("--recommendations", action="store_true", help="Show platform recommendations")
    parser.add_argument("--guide", help="Generate deployment guide for platform")
    
    args = parser.parse_args()
    
    deployer = OnlineDashboardDeployment()
    
    try:
        if args.recommendations:
            recommendations = await deployer.get_platform_recommendations()
            print("\n🎯 PLATFORM RECOMMENDATIONS:")
            for key, rec in recommendations.items():
                print(f"\n{key.title()}:")
                print(f"  Platform: {rec['platform']}")
                print(f"  Reason: {rec['reason']}")
                print(f"  URL: {rec['url']}")
        
        elif args.guide:
            guide = await deployer.create_deployment_guide(args.guide)
            print(f"\n📋 {args.guide.title()} Deployment Guide:")
            print(guide)
            
            # Save guide to file
            with open(f"{args.guide}_deployment_guide.md", "w") as f:
                f.write(guide)
            print(f"\n✅ Guide saved to {args.guide}_deployment_guide.md")
        
        else:
            # Deploy dashboard
            result = await deployer.deploy_dashboard(args.platform, args.domain)
            
            print("\n" + "="*60)
            print("MFM CORPORATION - DASHBOARD DEPLOYMENT")
            print("="*60)
            
            if result["success"]:
                print(f"✅ DEPLOYMENT PREPARATION COMPLETE")
                print(f"Platform: {result.get('platform', args.platform)}")
                
                if "instructions" in result:
                    print(f"\n📋 DEPLOYMENT INSTRUCTIONS:")
                    print(result["instructions"])
                
                if "next_steps" in result:
                    print(f"\n🔄 NEXT STEPS:")
                    for i, step in enumerate(result["next_steps"], 1):
                        print(f"  {i}. {step}")
                
                print(f"\n🎯 Your dashboard will be accessible online after following these steps!")
                
            else:
                print(f"❌ DEPLOYMENT FAILED")
                print(f"Error: {result.get('error', 'Unknown error')}")
            
            print("="*60)
            
            # Return appropriate exit code
            sys.exit(0 if result["success"] else 1)
    
    except KeyboardInterrupt:
        print("\n⚠️ Deployment interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Deployment failed with exception: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
