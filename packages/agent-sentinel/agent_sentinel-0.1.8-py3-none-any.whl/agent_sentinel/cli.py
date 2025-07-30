#!/usr/bin/env python3
"""
Sentinel CLI

Command-line interface for Sentinel security monitoring SDK.
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Optional

from .core.sentinel import AgentSentinel
from .logging.structured_logger import SecurityLogger


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Sentinel - Enterprise-grade security monitoring for AI agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start monitoring with config file
  sentinel monitor --config config.yaml

  # Validate configuration
  sentinel validate --config config.yaml

  # Show agent statistics
  sentinel stats --agent-id my_agent

  # Check security status
  sentinel security-check

  # Generate configuration template
  sentinel init --output config.yaml
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Monitor command
    monitor_parser = subparsers.add_parser("monitor", help="Start security monitoring")
    monitor_parser.add_argument(
        "--config", "-c",
        type=str,
        default="config.yaml",
        help="Configuration file path"
    )
    monitor_parser.add_argument(
        "--agent-id",
        type=str,
        help="Agent ID to monitor"
    )
    monitor_parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level"
    )
    monitor_parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as daemon process"
    )
    
    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate configuration")
    validate_parser.add_argument(
        "--config", "-c",
        type=str,
        required=True,
        help="Configuration file to validate"
    )
    validate_parser.add_argument(
        "--strict",
        action="store_true",
        help="Enable strict validation"
    )
    
    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Show monitoring statistics")
    stats_parser.add_argument(
        "--agent-id",
        type=str,
        help="Agent ID to show stats for"
    )
    stats_parser.add_argument(
        "--format",
        choices=["json", "table", "yaml"],
        default="table",
        help="Output format"
    )
    stats_parser.add_argument(
        "--config", "-c",
        type=str,
        default="config.yaml",
        help="Configuration file path"
    )
    
    # Security check command
    security_parser = subparsers.add_parser("security-check", help="Run security checks")
    security_parser.add_argument(
        "--config", "-c",
        type=str,
        default="config.yaml",
        help="Configuration file path"
    )
    security_parser.add_argument(
        "--output",
        type=str,
        help="Output file for security report"
    )
    
    # Unified report command
    report_parser = subparsers.add_parser("report", help="Generate unified monitoring report")
    report_parser.add_argument(
        "--config", "-c",
        type=str,
        default="config.yaml",
        help="Configuration file path"
    )
    report_parser.add_argument(
        "--agent-id",
        type=str,
        help="Agent ID to generate report for"
    )
    report_parser.add_argument(
        "--output",
        type=str,
        help="Output file path for unified report"
    )
    report_parser.add_argument(
        "--format",
        choices=["json", "markdown"],
        default="json",
        help="Report format"
    )
    
    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize Sentinel")
    init_parser.add_argument(
        "--output", "-o",
        type=str,
        default="config.yaml",
        help="Output configuration file path"
    )
    init_parser.add_argument(
        "--template",
        choices=["minimal", "production", "development"],
        default="production",
        help="Configuration template to use"
    )
    
    # Version command
    subparsers.add_parser("version", help="Show version information")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        if args.command == "monitor":
            run_monitor(args)
        elif args.command == "validate":
            run_validate(args)
        elif args.command == "stats":
            run_stats(args)
        elif args.command == "security-check":
            run_security_check(args)
        elif args.command == "report":
            run_report(args)
        elif args.command == "init":
            run_init(args)
        elif args.command == "version":
            run_version()
        else:
            parser.print_help()
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def run_monitor(args):
    """Run monitoring command"""
    print("🚀 Starting Sentinel monitoring...")
    
    try:
        # Initialize AgentSentinel
        sentinel = AgentSentinel(config_path=args.config)
        
        # Set up logging
        logger = SecurityLogger(
            name="sentinel_cli",
            level=args.log_level,
            json_format=True
        )
        
        logger.info("Sentinel monitoring started", extra={
            'config_file': args.config,
            'agent_id': args.agent_id,
            'log_level': args.log_level,
            'daemon_mode': args.daemon
        })
        
        print(f"✅ Monitoring started with config: {args.config}")
        if args.agent_id:
            print(f"🎯 Monitoring agent: {args.agent_id}")
        
        if args.daemon:
            print("🔄 Running in daemon mode...")
            # In a real implementation, this would fork to background
            # For now, just run in foreground
            try:
                # Keep running
                while True:
                    asyncio.sleep(1)
            except KeyboardInterrupt:
                pass
        else:
            print("📊 Monitoring active. Press Ctrl+C to stop.")
            try:
                # Keep running
                while True:
                    asyncio.sleep(1)
            except KeyboardInterrupt:
                pass
        
        logger.info("Sentinel monitoring stopped")
        print("🛑 Monitoring stopped")
        
    except Exception as e:
        print(f"❌ Failed to start monitoring: {e}")
        sys.exit(1)


def run_validate(args):
    """Run validation command"""
    print(f"🔍 Validating configuration: {args.config}")
    
    try:
        # Try to load configuration
        sentinel = AgentSentinel(config_path=args.config)
        
        # Validate configuration
        config = sentinel.config
        
        print("✅ Configuration validation passed!")
        print(f"   Agent ID: {config.agent_id}")
        print(f"   Environment: {config.environment}")
        print(f"   Detection enabled: {config.detection.enabled}")
        print(f"   Logging level: {config.logging.level}")
        
        if args.strict:
            print("\n🔒 Running strict validation...")
            # Additional strict validation checks
            validate_strict_config(config)
            print("✅ Strict validation passed!")
        
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        sys.exit(1)


def validate_strict_config(config):
    """Perform strict configuration validation"""
    # Check required fields
    if not config.agent_id:
        raise ValueError("Agent ID is required")
    
    if not config.detection.enabled:
        raise ValueError("Detection must be enabled for production")
    
    # Check security settings
    if config.environment == "production":
        if config.detection.confidence_threshold < 0.8:
            raise ValueError("Confidence threshold should be >= 0.8 for production")
        
        if not config.logging.json_format:
            raise ValueError("JSON logging format required for production")


def run_stats(args):
    """Run statistics command"""
    print(f"📊 Loading statistics from: {args.config}")
    
    try:
        # Initialize AgentSentinel
        sentinel = AgentSentinel(config_path=args.config)
        
        # Get statistics
        if args.agent_id:
            # Get specific agent stats
            stats = sentinel.get_agent_stats(args.agent_id)
        else:
            # Get overall stats
            stats = sentinel.get_overall_stats()
        
        # Format output
        if args.format == "json":
            print(json.dumps(stats, indent=2))
        elif args.format == "yaml":
            import yaml
            print(yaml.dump(stats, default_flow_style=False))
        else:
            # Table format
            print_stats_table(stats)
        
    except Exception as e:
        print(f"❌ Failed to load statistics: {e}")
        sys.exit(1)


def print_stats_table(stats):
    """Print statistics in table format"""
    print("\n📈 Sentinel Statistics")
    print("=" * 50)
    
    if "agents" in stats:
        print(f"Active Agents: {len(stats['agents'])}")
        for agent_id, agent_stats in stats["agents"].items():
            print(f"\n🎯 Agent: {agent_id}")
            print(f"   Method Calls: {agent_stats.get('total_method_calls', 0)}")
            print(f"   Security Events: {agent_stats.get('security_events', 0)}")
            print(f"   Sessions: {agent_stats.get('total_sessions', 0)}")
    
    if "overall" in stats:
        overall = stats["overall"]
        print(f"\n🌐 Overall Statistics")
        print(f"   Total Agents: {overall.get('total_agents', 0)}")
        print(f"   Total Events: {overall.get('total_events', 0)}")
        print(f"   Threat Types: {overall.get('threat_types', 0)}")
        print(f"   Uptime: {overall.get('uptime', 'N/A')}")


def run_security_check(args):
    """Run security check command"""
    print("🔒 Running security checks...")
    
    try:
        # Initialize AgentSentinel
        sentinel = AgentSentinel(config_path=args.config)
        
        # Run security checks
        security_report = sentinel.run_security_audit()
        
        # Print results
        print("\n🔍 Security Audit Results")
        print("=" * 50)
        
        for check_name, result in security_report.items():
            status = "✅" if result["passed"] else "❌"
            print(f"{status} {check_name}: {result['description']}")
            
            if not result["passed"]:
                print(f"   ⚠️  {result['recommendation']}")
        
        # Save report if requested
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(security_report, f, indent=2)
            print(f"\n📄 Security report saved to: {args.output}")
        
        # Exit with error if any checks failed
        failed_checks = [name for name, result in security_report.items() if not result["passed"]]
        if failed_checks:
            print(f"\n⚠️  {len(failed_checks)} security checks failed")
            sys.exit(1)
        else:
            print("\n✅ All security checks passed!")
        
    except Exception as e:
        print(f"❌ Security check failed: {e}")
        sys.exit(1)


def run_report(args):
    """Run unified report generation command"""
    print("📋 Generating unified monitoring report...")
    
    try:
        # Initialize AgentSentinel
        sentinel = AgentSentinel(config_path=args.config)
        
        # Override agent_id if specified
        if args.agent_id:
            sentinel.agent_id = args.agent_id
        
        # Generate unified report
        report_path = sentinel.generate_unified_report(args.output)
        
        print(f"✅ Unified report generated: {report_path}")
        print(f"📄 Report contains:")
        print(f"   - Session logs and monitoring data")
        print(f"   - Security events and threat analysis")
        print(f"   - Performance metrics and statistics")
        print(f"   - Actionable recommendations")
        
        # Show report summary if available
        try:
            import json
            with open(report_path, 'r') as f:
                report_data = json.load(f)
            
            summary = report_data.get('summary', {})
            if summary:
                print(f"\n📊 Report Summary:")
                print(f"   Status: {summary.get('status', 'UNKNOWN')}")
                print(f"   Security Events: {summary.get('total_security_events', 0)}")
                print(f"   Risk Score: {summary.get('risk_score', 0.0):.2f}")
                print(f"   Monitoring Duration: {summary.get('monitoring_duration', 0):.1f}s")
                
                recommendations = report_data.get('recommendations', [])
                if recommendations:
                    print(f"   Recommendations: {len(recommendations)}")
                    for i, rec in enumerate(recommendations[:3], 1):  # Show first 3
                        print(f"     {i}. {rec}")
                    if len(recommendations) > 3:
                        print(f"     ... and {len(recommendations) - 3} more")
        
        except Exception as e:
            print(f"⚠️  Could not display report summary: {e}")
        
    except Exception as e:
        print(f"❌ Failed to generate report: {e}")
        sys.exit(1)


def run_init(args):
    """Run initialization command"""
    print(f"🚀 Initializing Sentinel configuration...")
    
    try:
        # Generate configuration template
        config_template = generate_config_template(args.template)
        
        # Write to file
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            f.write(config_template)
        
        print(f"✅ Configuration template created: {args.output}")
        print(f"📝 Template type: {args.template}")
        print("\n📋 Next steps:")
        print("1. Review and customize the configuration")
        print("2. Set your agent ID and environment")
        print("3. Configure detection rules and logging")
        print("4. Run: sentinel validate --config config.yaml")
        print("5. Start monitoring: sentinel monitor --config config.yaml")
        
    except Exception as e:
        print(f"❌ Failed to create configuration: {e}")
        sys.exit(1)


def generate_config_template(template_type: str) -> str:
    """Generate configuration template"""
    if template_type == "minimal":
        return """sentinel:
  agent_id: "my_agent"
  environment: "development"
  
  detection:
    enabled: true
    confidence_threshold: 0.7
  
  logging:
    level: "INFO"
    format: "json"
    file: "logs/sentinel.log"
"""
    elif template_type == "development":
        return """sentinel:
  agent_id: "dev_agent"
  environment: "development"
  
  detection:
    enabled: true
    confidence_threshold: 0.6
    
    rules:
      sql_injection:
        enabled: true
        severity: "HIGH"
      xss_attack:
        enabled: true
        severity: "HIGH"
      prompt_injection:
        enabled: true
        severity: "MEDIUM"
    
    rate_limits:
      default_limit: 100
      default_window: 60
  
  logging:
    level: "DEBUG"
    format: "json"
    file: "logs/sentinel.log"
    max_size: 50MB
    backup_count: 3
  
  weave:
    enabled: false
  
  alerts:
    webhook_url: ""
    email:
      enabled: false
  
  dashboard:
    host: "localhost"
    port: 8000
    debug: true
"""
    else:  # production
        return """sentinel:
  agent_id: "production_agent"
  environment: "production"
  
  detection:
    enabled: true
    confidence_threshold: 0.8
    
    rules:
      sql_injection:
        enabled: true
        severity: "CRITICAL"
      xss_attack:
        enabled: true
        severity: "HIGH"
      command_injection:
        enabled: true
        severity: "CRITICAL"
      path_traversal:
        enabled: true
        severity: "HIGH"
      prompt_injection:
        enabled: true
        severity: "HIGH"
      data_exfiltration:
        enabled: true
        severity: "CRITICAL"
      
    rate_limits:
      default_limit: 100
      default_window: 60
      
      tools:
        exa_search:
          limit: 50
          window: 60
        web_scraper:
          limit: 20
          window: 60
        file_reader:
          limit: 30
          window: 60
  
  logging:
    level: "INFO"
    format: "json"
    file: "logs/sentinel.log"
    max_size: 100MB
    backup_count: 5
  
  weave:
    enabled: true
    project_name: "sentinel-production"
  
  alerts:
    webhook_url: "https://your-webhook-url.com"
    email:
      enabled: true
      smtp_server: "smtp.gmail.com"
      smtp_port: 587
      username: "your-email@gmail.com"
      password: "your-app-password"
      recipients: ["admin@company.com"]
  
  dashboard:
    host: "0.0.0.0"
    port: 8000
    debug: false
    ssl_enabled: true
    ssl_cert: "/path/to/cert.pem"
    ssl_key: "/path/to/key.pem"
"""


def run_version():
    """Show version information"""
    from . import __version__
    print(f"Sentinel v{__version__}")
    print("Enterprise-grade security monitoring for AI agents")


if __name__ == "__main__":
    main() 