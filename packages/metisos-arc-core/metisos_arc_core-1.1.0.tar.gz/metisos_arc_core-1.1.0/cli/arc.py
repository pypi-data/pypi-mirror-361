"""
ARC Core CLI Interface
Provides command-line tools for ARC consciousness engine operations.
"""

import click
import os
import json
import sys
from datetime import datetime
from arc_core import ARCConfig, ARCTrainer, MemorySystem, SafetySystem
from arc_core.teaching_packs import (
    TeachingPackManager, cmd_list_packs, cmd_install_pack, 
    cmd_uninstall_pack, cmd_validate_pack, cmd_pack_info, cmd_usage_stats
)
from arc_core.benchmark import BenchmarkEvaluator, BenchmarkSuite, run_benchmark_command, run_comparison_benchmark


@click.group()
@click.version_option(version='1.1.0')
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
        
        # Set device and model
        if device != 'auto':
            config.device = device
        config.model_name = base_model  # Update config with selected model
        
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
        
        # Initialize trainer and model
        trainer = ARCTrainer(config)
        trainer.initialize_model()
        
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
        
        # Initialize trainer and model
        trainer = ARCTrainer(config)
        trainer.initialize_model()
        
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
        
        # Initialize trainer and model
        trainer = ARCTrainer(config)
        trainer.initialize_model()
        
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
        
        # Initialize trainer and model
        trainer = ARCTrainer(config)
        trainer.initialize_model()
        
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
        
        click.echo("[SUCCESS] Health check completed")
        click.echo("[INFO] System ready for ARC operations")
        
    except Exception as e:
        click.echo(f"[ERROR] Health check failed: {str(e)}")
        sys.exit(1)


@cli.command()
@click.option('--suite', default='basic', help='Benchmark suite path or name')
@click.option('--model', help='Base model to benchmark (optional, for comparison)')
@click.option('--max-samples', type=int, help='Maximum samples to evaluate')
@click.option('--output', help='Output file path for results')
@click.option('--format', type=click.Choice(['json', 'markdown']), default='json', help='Output format')
@click.option('--config-file', default='.arc/config.json', help='Config file path')
def bench(suite, model, max_samples, output, format, config_file):
    """Run benchmark evaluation on ARC model"""
    try:
        # Load ARC configuration and trainer
        if not os.path.exists(config_file):
            click.echo("[ERROR] No ARC configuration found. Run 'arc init' first.")
            return
        
        config = ARCConfig.load(config_file)
        trainer = ARCTrainer(config)
        
        click.echo(f"[INFO] Running benchmark: {suite}")
        
        if model:
            # Comparison benchmark: base model vs ARC
            click.echo(f"[INFO] Comparing base model '{model}' vs ARC-enhanced model")
            comparison = run_comparison_benchmark(
                base_model=model,
                arc_trainer=trainer,
                suite_path=suite,
                max_samples=max_samples,
                output_path=output,
                format=format
            )
            
            # Show summary
            base_metrics = comparison['base']
            arc_metrics = comparison['arc']
            
            click.echo("\n[SUCCESS] Benchmark comparison completed!")
            click.echo(f"Base Model - Perplexity: {base_metrics.perplexity:.2f}, Latency: {base_metrics.avg_latency_ms:.1f}ms")
            click.echo(f"ARC Model  - Perplexity: {arc_metrics.perplexity:.2f}, Latency: {arc_metrics.avg_latency_ms:.1f}ms")
            
            # Calculate improvements
            if base_metrics.perplexity > 0:
                ppl_improvement = ((base_metrics.perplexity - arc_metrics.perplexity) / base_metrics.perplexity) * 100
                click.echo(f"[INFO] Perplexity improvement: {ppl_improvement:.1f}%")
            
            coherence_improvement = ((arc_metrics.coherence_score - base_metrics.coherence_score) / base_metrics.coherence_score) * 100 if base_metrics.coherence_score > 0 else 0
            click.echo(f"[INFO] Coherence improvement: {coherence_improvement:.1f}%")
            
        else:
            # Single model benchmark
            click.echo(f"[INFO] Evaluating ARC-enhanced model")
            metrics = run_benchmark_command(
                model_or_trainer=trainer,
                suite_path=suite,
                max_samples=max_samples,
                output_path=output,
                format=format
            )
            
            click.echo("\n[SUCCESS] Benchmark evaluation completed!")
            click.echo(f"Model: {metrics.model_name}")
            click.echo(f"Samples: {metrics.num_samples}")
            click.echo(f"Perplexity: {metrics.perplexity:.2f}")
            click.echo(f"Avg Latency: {metrics.avg_latency_ms:.1f} ms")
            click.echo(f"Peak Memory: {metrics.peak_memory_mb:.1f} MB")
            click.echo(f"Coherence Score: {metrics.coherence_score:.3f}")
            click.echo(f"Toxicity Score: {metrics.toxicity_score:.3f}")
            click.echo(f"Factual Accuracy: {metrics.factual_accuracy:.3f}")
        
        if output:
            click.echo(f"[INFO] Results saved to: {output}")
            
    except Exception as e:
        click.echo(f"[ERROR] Benchmark failed: {e}")
        if '--debug' in sys.argv:
            raise


# Teaching Pack Management Commands
@cli.group()
def pack():
    """Teaching pack management commands"""
    pass

@pack.command('list')
def pack_list():
    """List available teaching packs"""
    cmd_list_packs()

@pack.command()
@click.argument('pack_name')
@click.option('--force', is_flag=True, help='Force reinstall if already exists')
def install(pack_name, force):
    """Install a teaching pack"""
    cmd_install_pack(pack_name, force=force)

@pack.command()
@click.argument('pack_name')
def uninstall(pack_name):
    """Uninstall a teaching pack"""
    cmd_uninstall_pack(pack_name)

@pack.command()
@click.argument('pack_name')
def validate(pack_name):
    """Validate a teaching pack"""
    cmd_validate_pack(pack_name)

@pack.command()
@click.argument('pack_name') 
def info(pack_name):
    """Show detailed information about a teaching pack"""
    cmd_pack_info(pack_name)

@pack.command()
def stats():
    """Show teaching pack usage statistics"""
    cmd_usage_stats()

# Enhanced teach command with pack integration
@cli.command()
@click.argument('pack_name')
@click.option('--config-file', help='Path to configuration file')
@click.option('--epochs', default=1, help='Number of training epochs')
@click.option('--learning-rate', default=None, type=float, help='Learning rate override')
@click.option('--batch-size', default=None, type=int, help='Batch size override')
def teach_pack(pack_name, config_file, epochs, learning_rate, batch_size):
    """Train model using a specific teaching pack"""
    click.echo(f"[INFO] Training with teaching pack: {pack_name}")
    
    try:
        # Initialize pack manager
        manager = TeachingPackManager()
        
        # Check if pack exists
        pack_info = manager.get_pack_info(pack_name)
        if not pack_info:
            click.echo(f"[ERROR] Teaching pack '{pack_name}' not found")
            click.echo("Use 'arc pack list' to see available packs")
            click.echo("Use 'arc pack install {pack_name}' to install a pack")
            return
        
        click.echo(f"[INFO] Found pack: {pack_info['name']} v{pack_info['version']}")
        click.echo(f"[INFO] Description: {pack_info['description']}")
        click.echo(f"[INFO] Examples: {pack_info['total_examples']}")
        
        # Load configuration
        if config_file and os.path.exists(config_file):
            config = ARCConfig()
            config.load_from_file(config_file)
            click.echo(f"[OK] Configuration loaded from {config_file}")
        else:
            config = ARCConfig()
            click.echo("[OK] Using default configuration")
        
        # Override training parameters if provided
        if learning_rate:
            config.learning_rate = learning_rate
            click.echo(f"[INFO] Learning rate set to: {learning_rate}")
        
        if batch_size:
            config.batch_size = batch_size
            click.echo(f"[INFO] Batch size set to: {batch_size}")
        
        # Initialize trainer
        trainer = ARCTrainer(config)
        if not trainer.initialize_model():
            click.echo("[ERROR] Failed to initialize model")
            return
        
        # Get pack path for training
        pack_path = manager.get_pack_path(pack_name)
        if pack_info['type'] == 'builtin':
            # For built-in packs, install first if not already installed
            if not pack_path:
                click.echo(f"[INFO] Installing built-in pack: {pack_name}")
                if not manager.install_pack(pack_name):
                    click.echo(f"[ERROR] Failed to install pack: {pack_name}")
                    return
                pack_path = manager.get_pack_path(pack_name)
        
        if not pack_path:
            click.echo(f"[ERROR] Could not locate pack files for: {pack_name}")
            return
        
        click.echo(f"[INFO] Starting training with {epochs} epochs...")
        
        # Record training session in stats
        manager.record_training_session(pack_name)
        
        # Train with the pack
        success = trainer.train_with_pack(pack_path, epochs=epochs)
        
        if success:
            click.echo(f"[SUCCESS] Training completed successfully")
            click.echo(f"[INFO] Model updated with {pack_name} training data")
            
            # Show training statistics
            stats = trainer.get_training_stats()
            if stats:
                click.echo(f"[STATS] Total Updates: {stats.get('total_updates', 0)}")
                click.echo(f"[STATS] Avg Loss: {stats.get('avg_loss', 0.0):.4f}")
                click.echo(f"[STATS] Training Time: {stats.get('training_time', 0.0):.2f}s")
        else:
            click.echo(f"[ERROR] Training failed")
    
    except Exception as e:
        click.echo(f"[ERROR] Training failed: {e}")
        sys.exit(1)

# Enhanced test command with pack testing
@cli.command()
@click.option('--pack', help='Test against specific teaching pack')
@click.option('--config-file', help='Path to configuration file')
@click.option('--samples', default=10, help='Number of test samples')
def test_pack(pack, config_file, samples):
    """Test model performance against teaching pack examples"""
    if pack:
        click.echo(f"[INFO] Testing against teaching pack: {pack}")
    else:
        click.echo("[INFO] Running general model test")
    
    try:
        # Load configuration
        if config_file and os.path.exists(config_file):
            config = ARCConfig()
            config.load_from_file(config_file)
        else:
            config = ARCConfig()
        
        # Initialize trainer
        trainer = ARCTrainer(config)
        if not trainer.initialize_model():
            click.echo("[ERROR] Failed to initialize model")
            return
        
        if pack:
            # Test against specific teaching pack
            manager = TeachingPackManager()
            pack_info = manager.get_pack_info(pack)
            
            if not pack_info:
                click.echo(f"[ERROR] Teaching pack '{pack}' not found")
                return
            
            click.echo(f"[INFO] Testing against {pack_info['total_examples']} examples")
            
            # Get pack data for testing
            pack_path = manager.get_pack_path(pack)
            if pack_info['type'] == 'builtin' and not pack_path:
                # Install built-in pack if needed
                manager.install_pack(pack)
                pack_path = manager.get_pack_path(pack)
            
            if pack_path:
                pack_file = os.path.join(pack_path, 'pack.json')
                if os.path.exists(pack_file):
                    with open(pack_file, 'r') as f:
                        pack_data = json.load(f)
                    
                    examples = pack_data.get('examples', [])
                    test_samples = min(samples, len(examples))
                    
                    click.echo(f"[INFO] Testing {test_samples} samples...")
                    
                    correct = 0
                    total = 0
                    
                    for i, example in enumerate(examples[:test_samples]):
                        input_text = example.get('input', '')
                        expected = example.get('output', '')
                        
                        # Generate response
                        response = trainer.generate_response(input_text)
                        
                        # Simple similarity check (can be enhanced)
                        if response and expected.lower() in response.lower():
                            correct += 1
                        
                        total += 1
                        
                        click.echo(f"[TEST {i+1}] Input: {input_text[:50]}...")
                        click.echo(f"[TEST {i+1}] Expected: {expected[:50]}...")
                        click.echo(f"[TEST {i+1}] Got: {response[:50] if response else 'No response'}...")
                        click.echo()
                    
                    accuracy = (correct / total) * 100 if total > 0 else 0
                    click.echo(f"[RESULTS] Accuracy: {accuracy:.1f}% ({correct}/{total})")
        else:
            # General model test
            click.echo("[INFO] Running general model tests...")
            test_prompts = [
                "Hello, how are you?",
                "What is the weather like?", 
                "Explain photosynthesis",
                "What is 2+2?",
                "Tell me a joke"
            ]
            
            for i, prompt in enumerate(test_prompts[:samples], 1):
                response = trainer.generate_response(prompt)
                click.echo(f"[TEST {i}] Prompt: {prompt}")
                click.echo(f"[TEST {i}] Response: {response if response else 'No response'}")
                click.echo()
    
    except Exception as e:
        click.echo(f"[ERROR] Test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    cli()
