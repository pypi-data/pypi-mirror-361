"""
ARC Core CLI Interface
Provides command-line tools for ARC consciousness engine operations.
"""

import click
import os
import json
import sys
from datetime import datetime
from arc_core import ARCTrainer, ARCConfig


@click.group()
@click.version_option(version='1.0.7')
def cli():
    """ARC Core - Adaptive Recursive Consciousness Engine CLI"""
    pass


@cli.command()
@click.option('--base-model', required=True, help='Base model name or path')
@click.option('--device', default='auto', help='Device to use (auto, cpu, cuda)')
@click.option('--config-file', help='Path to configuration file')
def init(base_model, device, config_file):
    """Initialize ARC with a base model"""
    click.echo(f"[INFO] Initializing ARC with model: {base_model}")
    
    try:
        # Load or create config
        if config_file and os.path.exists(config_file):
            config = ARCConfig()
            config.load_from_file(config_file)
            click.echo(f"[OK] Configuration loaded from {config_file}")
        else:
            config = ARCConfig()
            click.echo("[OK] Using default configuration")
        
        # Set device
        if device != 'auto':
            config.device = device
        
        # Initialize trainer
        trainer = ARCTrainer(config)
        success = trainer.initialize_model(base_model)
        
        if success:
            click.echo(f"[SUCCESS] ARC initialized successfully with {base_model}")
            click.echo(f"[INFO] Device: {config.device}")
            
            # Save config for future use
            config_path = "arc_config.yaml"
            config.save_to_file(config_path)
            click.echo(f"[INFO] Configuration saved to {config_path}")
            
        else:
            click.echo("[ERROR] Failed to initialize ARC")
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"[ERROR] Initialization failed: {str(e)}")
        sys.exit(1)


@cli.command()
@click.option('--learning', is_flag=True, help='Enable learning mode')
@click.option('--config-file', default='arc_config.yaml', help='Configuration file')
def chat(learning, config_file):
    """Start interactive chat session"""
    click.echo("[INFO] Starting ARC chat session")
    
    try:
        # Load config
        if os.path.exists(config_file):
            config = ARCConfig()
            config.load_from_file(config_file)
            click.echo(f"[OK] Configuration loaded from {config_file}")
        else:
            click.echo("[ERROR] No configuration found. Run 'arc init' first.")
            sys.exit(1)
        
        # Initialize trainer
        trainer = ARCTrainer(config)
        # Note: Model initialization would need to be stored/loaded from previous init
        
        click.echo("[SUCCESS] ARC chat ready")
        click.echo("Type 'quit' to exit\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                if user_input.lower() in ['quit', 'exit', 'q']:
                    break
                
                if user_input:
                    response = trainer.generate_response(user_input)
                    click.echo(f"ARC: {response}\n")
                    
            except KeyboardInterrupt:
                break
        
        click.echo("\n[INFO] Chat session ended")
        
    except Exception as e:
        click.echo(f"[ERROR] Chat session failed: {str(e)}")
        sys.exit(1)


@cli.command()
@click.argument('pack_name')
@click.option('--config-file', default='arc_config.yaml', help='Configuration file')
def teach(pack_name, config_file):
    """Train using a teaching pack"""
    click.echo(f"[INFO] Teaching ARC with pack: {pack_name}")
    
    try:
        # Load config
        if os.path.exists(config_file):
            config = ARCConfig()
            config.load_from_file(config_file)
        else:
            click.echo("[ERROR] No configuration found. Run 'arc init' first.")
            sys.exit(1)
        
        # Initialize trainer
        trainer = ARCTrainer(config)
        
        # Load and train with teaching pack
        pack_path = f"arc_core/packs/{pack_name}"
        if os.path.exists(pack_path):
            result = trainer.train_with_pack(pack_name)
            click.echo(f"[SUCCESS] Training completed with pack: {pack_name}")
            click.echo(f"[INFO] Training result: {result}")
        else:
            click.echo(f"[ERROR] Teaching pack not found: {pack_name}")
            click.echo("Available packs: sentiment-basic")
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"[ERROR] Teaching failed: {str(e)}")
        sys.exit(1)


@cli.command()
@click.option('--pack', help='Test with specific pack')
@click.option('--config-file', default='arc_config.yaml', help='Configuration file')
def test(pack, config_file):
    """Test model performance"""
    click.echo("[INFO] Testing ARC performance")
    
    try:
        # Load config
        if os.path.exists(config_file):
            config = ARCConfig()
            config.load_from_file(config_file)
        else:
            click.echo("[ERROR] No configuration found. Run 'arc init' first.")
            sys.exit(1)
        
        # Initialize trainer
        trainer = ARCTrainer(config)
        
        # Run tests
        test_questions = [
            "What is consciousness?",
            "How do you learn new information?",
            "Explain the concept of intelligence."
        ]
        
        click.echo("[INFO] Running performance tests...\n")
        
        for i, question in enumerate(test_questions, 1):
            click.echo(f"Test {i}: {question}")
            response = trainer.generate_response(question)
            click.echo(f"Response: {response}\n")
        
        # Get training stats
        stats = trainer.get_training_stats()
        click.echo(f"[INFO] Training Statistics: {stats}")
        click.echo("[SUCCESS] Performance test completed")
        
    except Exception as e:
        click.echo(f"[ERROR] Testing failed: {str(e)}")
        sys.exit(1)


@cli.command()
@click.option('--path', required=True, help='Path to save model')
@click.option('--config-file', default='arc_config.yaml', help='Configuration file')
def save(path, config_file):
    """Save model to specified path"""
    click.echo(f"[INFO] Saving ARC model to: {path}")
    
    try:
        # Load config
        if os.path.exists(config_file):
            config = ARCConfig()
            config.load_from_file(config_file)
        else:
            click.echo("[ERROR] No configuration found. Run 'arc init' first.")
            sys.exit(1)
        
        # Initialize trainer
        trainer = ARCTrainer(config)
        
        # Save model
        trainer.save_model(path)
        click.echo(f"[SUCCESS] Model saved to {path}")
        
    except Exception as e:
        click.echo(f"[ERROR] Save failed: {str(e)}")
        sys.exit(1)


@cli.command()
@click.option('--config-file', default='arc_config.yaml', help='Configuration file')
def status(config_file):
    """Show current model status"""
    click.echo("[INFO] ARC System Status")
    click.echo("=" * 30)
    
    try:
        # Check config
        if os.path.exists(config_file):
            config = ARCConfig()
            config.load_from_file(config_file)
            click.echo(f"[OK] Configuration file: {config_file}")
            click.echo(f"[INFO] Device: {config.device}")
            click.echo(f"[INFO] Learning rate: {config.learning_rate}")
        else:
            click.echo("[WARNING] No configuration found")
            return
        
        # Initialize trainer for stats
        trainer = ARCTrainer(config)
        stats = trainer.get_training_stats()
        
        click.echo("\n[TRAINING STATS]:")
        for key, value in stats.items():
            click.echo(f"  {key}: {value}")
        
        click.echo("\n[SUCCESS] Status check completed")
        
    except Exception as e:
        click.echo(f"[ERROR] Status check failed: {str(e)}")
        sys.exit(1)


@cli.command()
def check():
    """Health check and system info"""
    click.echo("[INFO] ARC Core Health Check")
    click.echo("=" * 35)
    
    try:
        # Check Python version
        python_version = sys.version.split()[0]
        click.echo(f"[OK] Python version: {python_version}")
        
        # Check ARC Core import
        try:
            from arc_core import ARCTrainer, ARCConfig
            click.echo("[OK] ARC Core package: Available")
        except ImportError as e:
            click.echo(f"[ERROR] ARC Core package: {e}")
            return
        
        # Check PyTorch
        try:
            import torch
            click.echo(f"[OK] PyTorch version: {torch.__version__}")
            click.echo(f"[INFO] CUDA available: {torch.cuda.is_available()}")
        except ImportError:
            click.echo("[ERROR] PyTorch not found")
        
        # Check Transformers
        try:
            import transformers
            click.echo(f"[OK] Transformers version: {transformers.__version__}")
        except ImportError:
            click.echo("[ERROR] Transformers not found")
        
        # Test basic functionality
        try:
            config = ARCConfig()
            trainer = ARCTrainer(config)
            click.echo("[OK] ARC components: Functional")
        except Exception as e:
            click.echo(f"[ERROR] ARC components: {e}")
        
        click.echo("\n[SUCCESS] Health check completed")
        click.echo("[INFO] System ready for ARC operations")
        
    except Exception as e:
        click.echo(f"[ERROR] Health check failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    cli()
