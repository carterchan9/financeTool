#!/usr/bin/env python3
"""
Interactive Results Viewer for FinanceTool
==========================================

Simple Python script to view all generated results without Jupyter.

Usage:
    python view_results.py

Features:
    - View all visualizations in matplotlib window
    - Display model information
    - Show data summaries
    - Navigate with keyboard (n=next, p=previous, q=quit)

Author: FinanceTool Project
Last Updated: 2026-02-12
"""

import sys
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import joblib
from typing import List, Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import TICKERS


class ResultsViewer:
    """Interactive viewer for FinanceTool results."""

    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.data_dir = self.project_root / "data"
        self.models_dir = self.project_root / "models"
        self.figures_dir = self.project_root / "docs" / "figures"

        # Scan for files
        self.figure_files = self._get_figure_files()
        self.model_files = self._get_model_files()
        self.processed_files = self._get_processed_files()

        # State
        self.current_idx = 0

    def _get_figure_files(self) -> List[Path]:
        """Get all figure files."""
        if not self.figures_dir.exists():
            return []
        return sorted(list(self.figures_dir.glob("**/*.png")))

    def _get_model_files(self) -> List[Path]:
        """Get all model files."""
        if not self.models_dir.exists():
            return []
        return sorted(list(self.models_dir.glob("**/*.pkl")))

    def _get_processed_files(self) -> List[Path]:
        """Get all processed data files."""
        processed_dir = self.data_dir / "processed"
        if not processed_dir.exists():
            return []
        return sorted(list(processed_dir.glob("*.csv")))

    def print_summary(self):
        """Print summary of available results."""
        print("\n" + "="*70)
        print("  📊 FINANCETOOL RESULTS VIEWER")
        print("="*70)
        print(f"\n📁 Project Root: {self.project_root}")
        print(f"\n📈 Available Results:")
        print(f"   • Visualizations: {len(self.figure_files)}")
        print(f"   • Trained Models: {len(self.model_files)}")
        print(f"   • Processed Data: {len(self.processed_files)}")

        if not self.figure_files and not self.model_files and not self.processed_files:
            print("\n⚠️  No results found!")
            print("   Run 'python main.py' or 'python scripts/main_demo.py' first.")
            return False

        print("\n" + "="*70)
        return True

    def show_model_info(self):
        """Display information about trained models."""
        if not self.model_files:
            print("\n⚠️  No trained models found.")
            return

        print("\n" + "="*70)
        print("  🤖 TRAINED MODELS")
        print("="*70)

        for model_file in self.model_files:
            print(f"\n📦 Model: {model_file.name}")
            print("-" * 70)

            try:
                model = joblib.load(model_file)

                print(f"✅ Type: {type(model).__name__}")
                print(f"📊 Features: {model.n_features_in_}")
                print(f"🎯 Classes: {model.classes_}")

                # Get key parameters
                params = model.get_params()
                print(f"\n⚙️  Key Parameters:")
                key_params = ['C', 'class_weight', 'max_iter', 'random_state',
                            'n_estimators', 'max_depth']
                for param in key_params:
                    if param in params and params[param] is not None:
                        print(f"   • {param}: {params[param]}")

                # Feature coefficients if available
                if hasattr(model, 'coef_'):
                    print(f"\n📈 Feature Coefficients:")
                    feature_names = ['returns', 'ma_5', 'ma_20', 'volatility', 'price_to_ma']
                    for i, coef in enumerate(model.coef_[0]):
                        print(f"   • {feature_names[i]}: {coef:>10.6f}")

                # File size
                file_size = model_file.stat().st_size / 1024
                print(f"\n💾 File Size: {file_size:.2f} KB")

            except Exception as e:
                print(f"❌ Error loading model: {e}")

        print("\n" + "="*70)

    def show_data_summary(self):
        """Display summary of processed data."""
        if not self.processed_files:
            print("\n⚠️  No processed data found.")
            return

        print("\n" + "="*70)
        print("  📊 DATA SUMMARY")
        print("="*70)

        for pfile in self.processed_files:
            print(f"\n📈 {pfile.name}")
            print("-" * 70)

            try:
                df = pd.read_csv(pfile, index_col=0, parse_dates=True)

                print(f"📏 Shape: {df.shape[0]} rows × {df.shape[1]} columns")
                print(f"📅 Date Range: {df.index.min().date()} to {df.index.max().date()}")
                print(f"📋 Columns: {', '.join(df.columns[:6])}{'...' if len(df.columns) > 6 else ''}")

                # Target distribution if available
                if 'target' in df.columns:
                    target_counts = df['target'].value_counts()
                    total = len(df)
                    print(f"\n🎯 Target Distribution:")
                    print(f"   • Down days (0): {target_counts.get(0, 0)} ({target_counts.get(0, 0)/total*100:.1f}%)")
                    print(f"   • Up days (1): {target_counts.get(1, 0)} ({target_counts.get(1, 0)/total*100:.1f}%)")

                # Basic statistics for key features
                print(f"\n📊 Feature Statistics:")
                key_cols = ['returns', 'ma_5', 'volatility']
                available_cols = [col for col in key_cols if col in df.columns]
                if available_cols:
                    stats = df[available_cols].describe().loc[['mean', 'std', 'min', 'max']]
                    print(stats.to_string())

            except Exception as e:
                print(f"❌ Error loading data: {e}")

        print("\n" + "="*70)

    def view_figures_interactive(self):
        """View figures in interactive matplotlib window."""
        if not self.figure_files:
            print("\n⚠️  No visualizations found.")
            return

        print(f"\n🎨 Viewing {len(self.figure_files)} visualizations...")
        print("\nControls:")
        print("  • Click 'Next' or press 'n' for next image")
        print("  • Click 'Previous' or press 'p' for previous image")
        print("  • Press 'q' to quit")
        print("\n" + "="*70)

        # Create figure with buttons
        fig = plt.figure(figsize=(14, 10))
        ax_img = plt.subplot(111)
        plt.subplots_adjust(bottom=0.15)

        # Add navigation buttons
        ax_prev = plt.axes([0.3, 0.05, 0.15, 0.05])
        ax_next = plt.axes([0.55, 0.05, 0.15, 0.05])
        btn_prev = Button(ax_prev, 'Previous (p)')
        btn_next = Button(ax_next, 'Next (n)')

        def show_current():
            """Display current figure."""
            ax_img.clear()
            current_file = self.figure_files[self.current_idx]
            img = plt.imread(current_file)
            ax_img.imshow(img)
            ax_img.axis('off')
            title = f"[{self.current_idx + 1}/{len(self.figure_files)}] {current_file.stem}"
            ax_img.set_title(title, fontsize=12, fontweight='bold', pad=20)
            plt.draw()

        def next_image(event):
            """Show next image."""
            self.current_idx = (self.current_idx + 1) % len(self.figure_files)
            show_current()

        def prev_image(event):
            """Show previous image."""
            self.current_idx = (self.current_idx - 1) % len(self.figure_files)
            show_current()

        def on_key(event):
            """Handle keyboard input."""
            if event.key == 'n':
                next_image(event)
            elif event.key == 'p':
                prev_image(event)
            elif event.key == 'q':
                plt.close()

        # Connect events
        btn_next.on_clicked(next_image)
        btn_prev.on_clicked(prev_image)
        fig.canvas.mpl_connect('key_press_event', on_key)

        # Show first image
        show_current()
        plt.show()

    def view_figures_all(self):
        """View all figures at once in a grid."""
        if not self.figure_files:
            print("\n⚠️  No visualizations found.")
            return

        n_figs = len(self.figure_files)
        print(f"\n🎨 Displaying all {n_figs} visualizations in grid...")

        # Calculate grid dimensions
        n_cols = min(3, n_figs)
        n_rows = (n_figs + n_cols - 1) // n_cols

        fig = plt.figure(figsize=(18, 6 * n_rows))

        for idx, fig_file in enumerate(self.figure_files, 1):
            ax = plt.subplot(n_rows, n_cols, idx)
            img = plt.imread(fig_file)
            ax.imshow(img)
            ax.axis('off')
            ax.set_title(fig_file.stem, fontsize=10, fontweight='bold')

        plt.tight_layout()
        plt.show()

    def run(self, mode: str = 'interactive'):
        """
        Run the viewer.

        Args:
            mode: 'interactive' (one at a time), 'grid' (all at once), or 'info' (text only)
        """
        # Print summary
        if not self.print_summary():
            return

        # Show model info
        self.show_model_info()

        # Show data summary
        self.show_data_summary()

        # Show visualizations based on mode
        if mode == 'interactive':
            if self.figure_files:
                input("\nPress Enter to view visualizations...")
                self.view_figures_interactive()
        elif mode == 'grid':
            if self.figure_files:
                input("\nPress Enter to view visualizations...")
                self.view_figures_all()
        elif mode == 'info':
            # Just show info, no plots
            if self.figure_files:
                print("\n📋 Available Visualizations:")
                for idx, fig in enumerate(self.figure_files, 1):
                    print(f"   {idx}. {fig.name}")

        print("\n✅ Done!")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="View FinanceTool results interactively",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python view_results.py              # Interactive viewer (one at a time)
  python view_results.py --mode grid  # Grid view (all at once)
  python view_results.py --mode info  # Info only (no plots)
        """
    )
    parser.add_argument(
        '--mode',
        choices=['interactive', 'grid', 'info'],
        default='interactive',
        help='Viewing mode (default: interactive)'
    )

    args = parser.parse_args()

    # Run viewer
    viewer = ResultsViewer()
    viewer.run(mode=args.mode)


if __name__ == "__main__":
    main()
