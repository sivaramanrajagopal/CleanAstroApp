import os
from datetime import datetime
from typing import Dict, Any, List, Union
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor

class PDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        try:
            self.styles.add(ParagraphStyle(
                name='CustomTitle',
                parent=self.styles['Heading1'],
                fontSize=18,
                spaceAfter=20,
                alignment=TA_CENTER,
                textColor=HexColor('#2c3e50')
            ))
        except KeyError:
            pass
        
        # Subtitle style
        try:
            self.styles.add(ParagraphStyle(
                name='CustomSubtitle',
                parent=self.styles['Heading2'],
                fontSize=14,
                spaceAfter=12,
                textColor=HexColor('#34495e')
            ))
        except KeyError:
            pass
        
        # Section header style
        try:
            self.styles.add(ParagraphStyle(
                name='SectionHeader',
                parent=self.styles['Heading3'],
                fontSize=12,
                spaceAfter=8,
                textColor=HexColor('#2980b9')
            ))
        except KeyError:
            pass
        
        # Body text style
        try:
            self.styles.add(ParagraphStyle(
                name='BodyText',
                parent=self.styles['Normal'],
                fontSize=10,
                spaceAfter=6
            ))
        except KeyError:
            # Style already exists, skip
            pass
        
        # Table header style
        try:
            self.styles.add(ParagraphStyle(
                name='TableHeader',
                parent=self.styles['Normal'],
                fontSize=10,
                alignment=TA_CENTER,
                textColor=colors.white
            ))
        except KeyError:
            pass
    
    def create_header_footer(self, canvas_obj, doc, title):
        """Create header and footer for each page"""
        canvas_obj.saveState()
        
        # Header - Fixed positioning
        canvas_obj.setFont("Helvetica-Bold", 14)
        canvas_obj.setFillColor(HexColor('#2c3e50'))
        canvas_obj.drawString(72, doc.height + 72, "Vedic Astrology Dashboard")
        
        canvas_obj.setFont("Helvetica", 11)
        canvas_obj.setFillColor(HexColor('#7f8c8d'))
        canvas_obj.drawString(72, doc.height + 55, title)
        
        # Footer - Fixed positioning
        canvas_obj.setFont("Helvetica", 9)
        canvas_obj.setFillColor(HexColor('#95a5a6'))
        canvas_obj.drawString(72, 40, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        canvas_obj.drawRightString(doc.width + 72, 40, f"Page {canvas_obj.getPageNumber()}")
        
        canvas_obj.restoreState()
    
    def generate_chart_pdf(self, chart_data: Dict[str, Any], filename: Union[str, None] = None) -> str:
        """Generate PDF for birth chart analysis"""
        if not filename:
            filename = f"birth_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        doc = SimpleDocTemplate(filename, pagesize=A4, rightMargin=72, leftMargin=72, 
                              topMargin=72, bottomMargin=72)
        
        story = []
        
        # Title
        story.append(Paragraph("Birth Chart Analysis", self.styles['CustomTitle']))
        story.append(Spacer(1, 20))
        
        # Basic Information
        story.append(Paragraph("Personal Information", self.styles['CustomSubtitle']))
        basic_info = [
            ["Name", chart_data.get('name', 'N/A')],
            ["Date of Birth", chart_data.get('dob', 'N/A')],
            ["Time of Birth", chart_data.get('tob', 'N/A')],
            ["Place of Birth", chart_data.get('pob', 'N/A')],
            ["Latitude", f"{chart_data.get('latitude', 'N/A')}°"],
            ["Longitude", f"{chart_data.get('longitude', 'N/A')}°"]
        ]
        
        basic_table = Table(basic_info, colWidths=[2*inch, 4*inch])
        basic_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(basic_table)
        story.append(Spacer(1, 20))
        
        # Planetary Positions
        story.append(Paragraph("Planetary Positions", self.styles['CustomSubtitle']))
        if 'planets' in chart_data:
            planet_data = [["Planet", "Sign", "Degree", "House", "Nakshatra", "Strength"]]
            for planet in chart_data['planets']:
                planet_data.append([
                    planet.get('name', ''),
                    planet.get('sign', ''),
                    f"{planet.get('degree', 0):.2f}°",
                    str(planet.get('house', '')),
                    planet.get('nakshatra', ''),
                    f"{planet.get('strength', 0):.1f}%"
                ])
            
            planet_table = Table(planet_data, colWidths=[0.8*inch, 0.8*inch, 0.8*inch, 0.6*inch, 1.2*inch, 0.8*inch])
            planet_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#e74c3c')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(planet_table)
            story.append(Spacer(1, 20))
        
        # House Analysis
        story.append(Paragraph("House Analysis", self.styles['CustomSubtitle']))
        if 'houses' in chart_data:
            house_data = [["House", "Sign", "Lord", "Strength", "Status"]]
            for i, house in enumerate(chart_data['houses'], 1):
                house_data.append([
                    str(i),
                    house.get('sign', ''),
                    house.get('lord', ''),
                    f"{house.get('strength', 0):.1f}%",
                    house.get('status', '')
                ])
            
            house_table = Table(house_data, colWidths=[0.6*inch, 1*inch, 0.8*inch, 0.8*inch, 1.2*inch])
            house_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#27ae60')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(house_table)
            story.append(Spacer(1, 20))
        
        # Yogas
        if 'yogas' in chart_data and chart_data['yogas']:
            story.append(Paragraph("Yogas (Planetary Combinations)", self.styles['CustomSubtitle']))
            yoga_data = [["Yoga", "Planets", "Effect"]]
            for yoga in chart_data['yogas']:
                yoga_data.append([
                    yoga.get('name', ''),
                    yoga.get('planets', ''),
                    yoga.get('effect', '')
                ])
            
            yoga_table = Table(yoga_data, colWidths=[2*inch, 1.5*inch, 2.5*inch])
            yoga_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#f39c12')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(yoga_table)
            story.append(Spacer(1, 20))
        
        # Overall Health Score
        if 'overall_health' in chart_data:
            story.append(Paragraph("Overall Chart Health", self.styles['CustomSubtitle']))
            health_text = f"Overall Health Score: {chart_data['overall_health']:.1f}%"
            story.append(Paragraph(health_text, self.styles['BodyText']))
            story.append(Spacer(1, 10))
        
        # Build PDF
        doc.build(story, onFirstPage=lambda canvas, doc: self.create_header_footer(canvas, doc, "Birth Chart Analysis"))
        
        return filename
    
    def generate_dasha_pdf(self, dasha_data: Dict[str, Any], filename: Union[str, None] = None) -> str:
        """Generate PDF for Dasha analysis"""
        if not filename:
            filename = f"dasha_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        doc = SimpleDocTemplate(filename, pagesize=A4, rightMargin=72, leftMargin=72, 
                              topMargin=72, bottomMargin=72)
        
        story = []
        
        # Title
        story.append(Paragraph("Vimshottari Dasha Analysis", self.styles['CustomTitle']))
        story.append(Spacer(1, 20))
        
        # Basic Information
        story.append(Paragraph("Birth Information", self.styles['CustomSubtitle']))
        basic_info = [
            ["Name", dasha_data.get('name', 'N/A')],
            ["Date of Birth", dasha_data.get('dob', 'N/A')],
            ["Birth Nakshatra", dasha_data.get('birth_nakshatra', 'N/A')],
            ["Nakshatra Lord", dasha_data.get('nakshatra_lord', 'N/A')]
        ]
        
        basic_table = Table(basic_info, colWidths=[2*inch, 4*inch])
        basic_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(basic_table)
        story.append(Spacer(1, 20))
        
        # Current Dasha
        if 'current_dasha' in dasha_data:
            story.append(Paragraph("Current Dasha Period", self.styles['CustomSubtitle']))
            current_dasha = dasha_data['current_dasha']
            dasha_info = [
                ["Dasha Lord", current_dasha.get('lord', 'N/A')],
                ["Start Date", current_dasha.get('start_date', 'N/A')],
                ["End Date", current_dasha.get('end_date', 'N/A')],
                ["Duration", current_dasha.get('duration', 'N/A')]
            ]
            
            dasha_table = Table(dasha_info, colWidths=[2*inch, 4*inch])
            dasha_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), HexColor('#e74c3c')),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(dasha_table)
            story.append(Spacer(1, 20))
        
        # Antardasha Periods
        if 'antardashas' in dasha_data and dasha_data['antardashas']:
            story.append(Paragraph("Antardasha Periods", self.styles['CustomSubtitle']))
            antardasha_data = [["Lord", "Start Date", "End Date", "Duration"]]
            
            for antardasha in dasha_data['antardashas']:
                antardasha_data.append([
                    antardasha.get('lord', ''),
                    antardasha.get('start_date', ''),
                    antardasha.get('end_date', ''),
                    antardasha.get('duration', '')
                ])
            
            antardasha_table = Table(antardasha_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
            antardasha_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#27ae60')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(antardasha_table)
            story.append(Spacer(1, 20))
        
        # Build PDF
        doc.build(story, onFirstPage=lambda canvas, doc: self.create_header_footer(canvas, doc, "Dasha Analysis"))
        
        return filename
    
    def generate_shadbala_pdf(self, shadbala_data: Dict[str, Any], filename: Union[str, None] = None) -> str:
        """Generate PDF for Shadbala analysis"""
        if not filename:
            filename = f"shadbala_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        doc = SimpleDocTemplate(filename, pagesize=A4, rightMargin=72, leftMargin=72, 
                              topMargin=72, bottomMargin=72)
        
        story = []
        
        # Title
        story.append(Paragraph("Shadbala Analysis", self.styles['CustomTitle']))
        story.append(Spacer(1, 20))
        
        # Basic Information
        story.append(Paragraph("Personal Information", self.styles['CustomSubtitle']))
        basic_info = [
            ["Name", shadbala_data.get('name', 'N/A')],
            ["Date of Birth", shadbala_data.get('dob', 'N/A')],
            ["Time of Birth", shadbala_data.get('tob', 'N/A')],
            ["Place of Birth", shadbala_data.get('pob', 'N/A')]
        ]
        
        basic_table = Table(basic_info, colWidths=[2*inch, 4*inch])
        basic_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(basic_table)
        story.append(Spacer(1, 20))
        
        # Shadbala Components
        if 'shadbala_components' in shadbala_data:
            story.append(Paragraph("Shadbala Components", self.styles['CustomSubtitle']))
            components_data = [["Component", "Description", "Strength"]]
            
            for component in shadbala_data['shadbala_components']:
                components_data.append([
                    component.get('name', ''),
                    component.get('description', ''),
                    f"{component.get('strength', 0):.1f}%"
                ])
            
            components_table = Table(components_data, colWidths=[1.5*inch, 3*inch, 1.5*inch])
            components_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#e74c3c')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(components_table)
            story.append(Spacer(1, 20))
        
        # Planet Strengths
        if 'planet_strengths' in shadbala_data:
            story.append(Paragraph("Planet Strengths", self.styles['CustomSubtitle']))
            planet_data = [["Planet", "Total Strength", "Status"]]
            
            for planet in shadbala_data['planet_strengths']:
                planet_data.append([
                    planet.get('name', ''),
                    f"{planet.get('total_strength', 0):.1f}%",
                    planet.get('status', '')
                ])
            
            planet_table = Table(planet_data, colWidths=[1.5*inch, 2*inch, 2.5*inch])
            planet_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#27ae60')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(planet_table)
            story.append(Spacer(1, 20))
        
        # Build PDF
        doc.build(story, onFirstPage=lambda canvas, doc: self.create_header_footer(canvas, doc, "Shadbala Analysis"))
        
        return filename
    
    def generate_cosmic_connections_pdf(self, cosmic_data: Dict[str, Any], filename: Union[str, None] = None) -> str:
        """Generate PDF for Cosmic Connections analysis"""
        if not filename:
            filename = f"cosmic_connections_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        doc = SimpleDocTemplate(filename, pagesize=A4, rightMargin=72, leftMargin=72, 
                              topMargin=72, bottomMargin=72)
        
        story = []
        
        # Title
        story.append(Paragraph("Cosmic Connections Analysis", self.styles['CustomTitle']))
        story.append(Spacer(1, 20))
        
        # Basic Information
        story.append(Paragraph("Personal Information", self.styles['CustomSubtitle']))
        basic_info = [
            ["Name", cosmic_data.get('name', 'N/A')],
            ["Date of Birth", cosmic_data.get('dob', 'N/A')],
            ["Time of Birth", cosmic_data.get('tob', 'N/A')],
            ["Place of Birth", cosmic_data.get('pob', 'N/A')]
        ]
        
        basic_table = Table(basic_info, colWidths=[2*inch, 4*inch])
        basic_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))
        story.append(basic_table)
        story.append(Spacer(1, 20))
        
        # Add page break before planet details for better organization
        story.append(PageBreak())
        
        # Planet Details
        if 'planets' in cosmic_data:
            story.append(Paragraph("Planet Details", self.styles['CustomSubtitle']))
            story.append(Spacer(1, 10))
            planet_data = [["Planet", "Sign", "House", "Nakshatra", "Pada", "Lord"]]
            
            for planet in cosmic_data['planets']:
                planet_data.append([
                    planet.get('name', ''),
                    planet.get('sign', ''),
                    str(planet.get('house', '')),
                    planet.get('nakshatra', ''),
                    str(planet.get('pada', '')),
                    planet.get('lord', '')
                ])
            
            # Improved column widths for better readability
            planet_table = Table(planet_data, colWidths=[1.3*inch, 1.3*inch, 0.7*inch, 1.6*inch, 0.7*inch, 1.4*inch])
            planet_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#e74c3c')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('WORDWRAP', (0, 0), (-1, -1), True)  # Enable word wrapping
            ]))
            story.append(planet_table)
            story.append(Spacer(1, 20))
        
        # Connection Analysis
        if 'connections' in cosmic_data:
            story.append(Paragraph("Cosmic Connections", self.styles['CustomSubtitle']))
            story.append(Spacer(1, 10))
            
            # Split connections by type for better organization
            connection_types = {}
            for connection in cosmic_data['connections']:
                conn_type = connection.get('type', 'Other')
                if conn_type not in connection_types:
                    connection_types[conn_type] = []
                connection_types[conn_type].append(connection)
            
            for conn_type, connections in connection_types.items():
                # Add section header
                story.append(Paragraph(f"{conn_type}", self.styles['CustomSubtitle']))
                story.append(Spacer(1, 5))
                
                connection_data = [["Details", "Strength"]]
                
                for connection in connections:
                    details = connection.get('details', '')
                    strength = connection.get('strength', '')
                    
                    # Smart truncation - keep complete words
                    if len(details) > 100:
                        # Find the last space before 100 characters
                        truncated = details[:100]
                        last_space = truncated.rfind(' ')
                        if last_space > 80:  # Only truncate if we can find a good break point
                            details = details[:last_space] + "..."
                        else:
                            details = details[:97] + "..."
                    
                    connection_data.append([details, strength])
                
                # Use wider columns for better text display with word wrapping
                connection_table = Table(connection_data, colWidths=[4.2*inch, 1.8*inch])
                connection_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), HexColor('#27ae60')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (0, -1), 'LEFT'),  # Details left-aligned
                    ('ALIGN', (1, 0), (1, -1), 'CENTER'),  # Strength center-aligned
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 7),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Top alignment for multi-line text
                    ('WORDWRAP', (0, 0), (-1, -1), True)  # Enable word wrapping
                ]))
                story.append(connection_table)
                story.append(Spacer(1, 15))
            
            story.append(Spacer(1, 20))
        
        # Add summary section
        story.append(PageBreak())
        story.append(Paragraph("Analysis Summary", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 15))
        
        summary_text = """
        This Cosmic Connections analysis reveals the intricate relationships between planets, houses, and nakshatras in your birth chart. 
        The connections show how different planetary energies interact and influence various aspects of your life.
        
        <b>Key findings include:</b>
        • Planet-House Lord connections show which planets rule which houses
        • House Lord placements reveal where your house lords are positioned  
        • Nakshatra Lord connections show nakshatra lord relationships
        • Planet aspects demonstrate how planets influence other houses
        
        This analysis follows traditional Vedic astrology principles as outlined by Parashara.
        """
        
        story.append(Paragraph(summary_text, self.styles['BodyText']))
        story.append(Spacer(1, 25))
        
        # Build PDF
        doc.build(story, onFirstPage=lambda canvas, doc: self.create_header_footer(canvas, doc, "Cosmic Connections"))
        
        return filename
    
    def generate_transits_pdf(self, transit_data: Dict[str, Any], filename: Union[str, None] = None) -> str:
        """Generate PDF for Transit analysis"""
        if not filename:
            filename = f"transit_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        doc = SimpleDocTemplate(filename, pagesize=A4, rightMargin=72, leftMargin=72, 
                              topMargin=72, bottomMargin=72)
        
        story = []
        
        # Title
        story.append(Paragraph("Transit Analysis", self.styles['CustomTitle']))
        story.append(Spacer(1, 20))
        
        # Basic Information
        story.append(Paragraph("Personal Information", self.styles['CustomSubtitle']))
        basic_info = [
            ["Name", transit_data.get('name', 'N/A')],
            ["Date of Birth", transit_data.get('dob', 'N/A')],
            ["Analysis Date", transit_data.get('analysis_date', 'N/A')]
        ]
        
        basic_table = Table(basic_info, colWidths=[2*inch, 4*inch])
        basic_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(basic_table)
        story.append(Spacer(1, 20))
        
        # Transit Details
        if 'transits' in transit_data:
            story.append(Paragraph("Current Transits", self.styles['CustomSubtitle']))
            transit_details = [["Planet", "From Sign", "To Sign", "House", "Effect"]]
            
            for transit in transit_data['transits']:
                transit_details.append([
                    transit.get('planet', ''),
                    transit.get('from_sign', ''),
                    transit.get('to_sign', ''),
                    str(transit.get('house', '')),
                    transit.get('effect', '')
                ])
            
            transit_table = Table(transit_details, colWidths=[1*inch, 1*inch, 1*inch, 0.8*inch, 2.2*inch])
            transit_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#e74c3c')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 7),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(transit_table)
            story.append(Spacer(1, 20))
        
        # Build PDF
        doc.build(story, onFirstPage=lambda canvas, doc: self.create_header_footer(canvas, doc, "Transit Analysis"))
        
        return filename
    
    def generate_compatibility_pdf(self, compatibility_data: Dict[str, Any], filename: Union[str, None] = None) -> str:
        """Generate PDF for Compatibility analysis"""
        if not filename:
            filename = f"compatibility_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        doc = SimpleDocTemplate(filename, pagesize=A4, rightMargin=72, leftMargin=72, 
                              topMargin=72, bottomMargin=72)
        
        story = []
        
        # Title
        story.append(Paragraph("Compatibility Analysis", self.styles['CustomTitle']))
        story.append(Spacer(1, 20))
        
        # Basic Information
        story.append(Paragraph("Personal Information", self.styles['CustomSubtitle']))
        basic_info = [
            ["Person 1", compatibility_data.get('person1_name', 'N/A')],
            ["Person 2", compatibility_data.get('person2_name', 'N/A')],
            ["Analysis Date", compatibility_data.get('analysis_date', 'N/A')]
        ]
        
        basic_table = Table(basic_info, colWidths=[2*inch, 4*inch])
        basic_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(basic_table)
        story.append(Spacer(1, 20))
        
        # Compatibility Scores
        if 'compatibility_scores' in compatibility_data:
            story.append(Paragraph("Compatibility Scores", self.styles['CustomSubtitle']))
            scores_data = [["Aspect", "Score", "Status"]]
            
            for score in compatibility_data['compatibility_scores']:
                scores_data.append([
                    score.get('aspect', ''),
                    f"{score.get('score', 0):.1f}%",
                    score.get('status', '')
                ])
            
            scores_table = Table(scores_data, colWidths=[2*inch, 1.5*inch, 2.5*inch])
            scores_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#e74c3c')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(scores_table)
            story.append(Spacer(1, 20))
        
        # Overall Compatibility
        if 'overall_compatibility' in compatibility_data:
            story.append(Paragraph("Overall Compatibility", self.styles['CustomSubtitle']))
            overall_text = f"Overall Compatibility Score: {compatibility_data['overall_compatibility']:.1f}%"
            story.append(Paragraph(overall_text, self.styles['BodyText']))
            story.append(Spacer(1, 10))
        
        # Build PDF
        doc.build(story, onFirstPage=lambda canvas, doc: self.create_header_footer(canvas, doc, "Compatibility Analysis"))
        
        return filename

# Global PDF generator instance
pdf_generator = PDFGenerator() 