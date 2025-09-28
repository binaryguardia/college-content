"""
JalDoot Visualization Service
Create charts and graphs for groundwater data
"""

import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
import base64
import io
from datetime import datetime

# Set style for better looking plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class VisualizationService:
    """Service for creating groundwater data visualizations"""
    
    def __init__(self):
        self.colors = {
            'primary': '#2E86AB',
            'secondary': '#A23B72',
            'accent': '#F18F01',
            'success': '#C73E1D',
            'warning': '#FFD23F',
            'info': '#06FFA5'
        }
        
        # Set matplotlib to use a non-interactive backend
        plt.switch_backend('Agg')
    
    def create_groundwater_level_chart(self, data: List[Dict], region: str, year: int) -> str:
        """Create a line chart showing groundwater levels over time"""
        if not data:
            return self._create_no_data_chart("No groundwater data available")
        
        # Convert data to DataFrame
        df = pd.DataFrame(data)
        
        # Create the plot
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot groundwater levels
        if 'month' in df.columns and df['month'].notna().any():
            # Monthly data
            monthly_data = df.groupby('month')['measurement'].mean()
            ax.plot(monthly_data.index, monthly_data.values, 
                   marker='o', linewidth=2, markersize=8, color=self.colors['primary'])
            ax.set_xlabel('Month')
            ax.set_xticks(range(1, 13))
            ax.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
        else:
            # Single data point or no monthly data
            ax.bar(range(len(df)), df['measurement'], color=self.colors['primary'], alpha=0.7)
            ax.set_xlabel('Data Points')
        
        ax.set_ylabel('Groundwater Level (m)')
        ax.set_title(f'Groundwater Levels in {region} - {year}', fontsize=16, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        # Add value labels on points
        for i, v in enumerate(df['measurement']):
            ax.annotate(f'{v:.1f}m', (i, v), textcoords="offset points", 
                       xytext=(0,10), ha='center')
        
        return self._fig_to_base64(fig)
    
    def create_regional_comparison_chart(self, data: List[Dict]) -> str:
        """Create a bar chart comparing groundwater levels across regions"""
        if not data:
            return self._create_no_data_chart("No regional data available")
        
        df = pd.DataFrame(data)
        
        # Group by region and calculate average
        regional_avg = df.groupby('region')['measurement'].mean().sort_values(ascending=True)
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        bars = ax.barh(regional_avg.index, regional_avg.values, 
                      color=self.colors['primary'], alpha=0.8)
        
        ax.set_xlabel('Average Groundwater Level (m)')
        ax.set_title('Groundwater Levels Comparison Across Regions', 
                    fontsize=16, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='x')
        
        # Add value labels
        for i, v in enumerate(regional_avg.values):
            ax.text(v + 0.1, i, f'{v:.1f}m', va='center', fontweight='bold')
        
        return self._fig_to_base64(fig)
    
    def create_aquifer_type_chart(self, data: List[Dict]) -> str:
        """Create a pie chart showing distribution by aquifer type"""
        if not data:
            return self._create_no_data_chart("No aquifer data available")
        
        df = pd.DataFrame(data)
        
        if 'aquifer_type' not in df.columns or df['aquifer_type'].isna().all():
            return self._create_no_data_chart("No aquifer type information available")
        
        # Count aquifer types
        aquifer_counts = df['aquifer_type'].value_counts()
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        colors = [self.colors['primary'], self.colors['secondary'], 
                 self.colors['accent'], self.colors['success']]
        
        wedges, texts, autotexts = ax.pie(aquifer_counts.values, 
                                         labels=aquifer_counts.index,
                                         autopct='%1.1f%%',
                                         colors=colors[:len(aquifer_counts)],
                                         startangle=90)
        
        ax.set_title('Distribution by Aquifer Type', fontsize=16, fontweight='bold')
        
        # Make percentage text bold
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        return self._fig_to_base64(fig)
    
    def create_well_type_chart(self, data: List[Dict]) -> str:
        """Create a bar chart showing distribution by well type"""
        if not data:
            return self._create_no_data_chart("No well type data available")
        
        df = pd.DataFrame(data)
        
        if 'well_type' not in df.columns or df['well_type'].isna().all():
            return self._create_no_data_chart("No well type information available")
        
        well_counts = df['well_type'].value_counts()
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        bars = ax.bar(well_counts.index, well_counts.values, 
                     color=self.colors['secondary'], alpha=0.8)
        
        ax.set_xlabel('Well Type')
        ax.set_ylabel('Number of Wells')
        ax.set_title('Distribution by Well Type', fontsize=16, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                   f'{int(height)}', ha='center', va='bottom', fontweight='bold')
        
        return self._fig_to_base64(fig)
    
    def create_data_quality_chart(self, data: List[Dict]) -> str:
        """Create a chart showing data quality distribution"""
        if not data:
            return self._create_no_data_chart("No data quality information available")
        
        df = pd.DataFrame(data)
        
        if 'data_quality' not in df.columns or df['data_quality'].isna().all():
            return self._create_no_data_chart("No data quality information available")
        
        quality_counts = df['data_quality'].value_counts()
        
        # Define colors for quality levels
        quality_colors = {
            'High': self.colors['success'],
            'Medium': self.colors['warning'],
            'Low': self.colors['info']
        }
        
        colors = [quality_colors.get(q, self.colors['primary']) for q in quality_counts.index]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        bars = ax.bar(quality_counts.index, quality_counts.values, color=colors, alpha=0.8)
        
        ax.set_xlabel('Data Quality')
        ax.set_ylabel('Number of Records')
        ax.set_title('Data Quality Distribution', fontsize=16, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                   f'{int(height)}', ha='center', va='bottom', fontweight='bold')
        
        return self._fig_to_base64(fig)
    
    def create_interactive_plotly_chart(self, data: List[Dict], region: str, year: int) -> str:
        """Create an interactive Plotly chart"""
        if not data:
            return self._create_no_data_chart("No data available for interactive chart")
        
        df = pd.DataFrame(data)
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Groundwater Levels', 'Aquifer Types', 'Well Types', 'Data Quality'),
            specs=[[{"type": "scatter"}, {"type": "pie"}],
                   [{"type": "bar"}, {"type": "bar"}]]
        )
        
        # Groundwater levels over time
        if 'month' in df.columns and df['month'].notna().any():
            monthly_data = df.groupby('month')['measurement'].mean()
            fig.add_trace(
                go.Scatter(x=monthly_data.index, y=monthly_data.values,
                          mode='lines+markers', name='Groundwater Level',
                          line=dict(color=self.colors['primary'], width=3)),
                row=1, col=1
            )
        
        # Aquifer types pie chart
        if 'aquifer_type' in df.columns and df['aquifer_type'].notna().any():
            aquifer_counts = df['aquifer_type'].value_counts()
            fig.add_trace(
                go.Pie(labels=aquifer_counts.index, values=aquifer_counts.values,
                      name="Aquifer Types"),
                row=1, col=2
            )
        
        # Well types bar chart
        if 'well_type' in df.columns and df['well_type'].notna().any():
            well_counts = df['well_type'].value_counts()
            fig.add_trace(
                go.Bar(x=well_counts.index, y=well_counts.values,
                      name="Well Types", marker_color=self.colors['secondary']),
                row=2, col=1
            )
        
        # Data quality bar chart
        if 'data_quality' in df.columns and df['data_quality'].notna().any():
            quality_counts = df['data_quality'].value_counts()
            fig.add_trace(
                go.Bar(x=quality_counts.index, y=quality_counts.values,
                      name="Data Quality", marker_color=self.colors['accent']),
                row=2, col=2
            )
        
        fig.update_layout(
            title_text=f"Groundwater Data Dashboard - {region} {year}",
            showlegend=False,
            height=800
        )
        
        return fig.to_html(include_plotlyjs='cdn')
    
    def create_summary_statistics_chart(self, data: List[Dict]) -> str:
        """Create a chart showing summary statistics"""
        if not data:
            return self._create_no_data_chart("No data available for statistics")
        
        df = pd.DataFrame(data)
        
        # Calculate statistics
        stats = {
            'Mean': df['measurement'].mean(),
            'Median': df['measurement'].median(),
            'Min': df['measurement'].min(),
            'Max': df['measurement'].max(),
            'Std Dev': df['measurement'].std()
        }
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        bars = ax.bar(stats.keys(), stats.values(), 
                     color=self.colors['primary'], alpha=0.8)
        
        ax.set_ylabel('Groundwater Level (m)')
        ax.set_title('Summary Statistics', fontsize=16, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                   f'{height:.2f}m', ha='center', va='bottom', fontweight='bold')
        
        return self._fig_to_base64(fig)
    
    def _create_no_data_chart(self, message: str) -> str:
        """Create a chart showing no data message"""
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, message, ha='center', va='center', 
               fontsize=16, fontweight='bold', transform=ax.transAxes)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        ax.set_title('No Data Available', fontsize=18, fontweight='bold')
        
        return self._fig_to_base64(fig)
    
    def _fig_to_base64(self, fig) -> str:
        """Convert matplotlib figure to base64 string"""
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close(fig)
        
        return f"data:image/png;base64,{image_base64}"
    
    def create_comprehensive_dashboard(self, data: List[Dict], region: str, year: int) -> Dict[str, str]:
        """Create a comprehensive dashboard with multiple visualizations"""
        dashboard = {}
        
        try:
            dashboard['groundwater_levels'] = self.create_groundwater_level_chart(data, region, year)
            dashboard['aquifer_types'] = self.create_aquifer_type_chart(data)
            dashboard['well_types'] = self.create_well_type_chart(data)
            dashboard['data_quality'] = self.create_data_quality_chart(data)
            dashboard['summary_stats'] = self.create_summary_statistics_chart(data)
            dashboard['interactive'] = self.create_interactive_plotly_chart(data, region, year)
            
        except Exception as e:
            print(f"Error creating dashboard: {e}")
            dashboard['error'] = f"Error creating visualizations: {str(e)}"
        
        return dashboard
