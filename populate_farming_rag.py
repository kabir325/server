#!/usr/bin/env python3
"""
Populate RAG with sample farming knowledge
Run this to add initial farming documents to your RAG system
"""

import requests
import json

SERVER_URL = "http://localhost:5001"

# Sample farming documents
FARMING_DOCUMENTS = [
    {
        "title": "Wheat Irrigation Schedule",
        "content": """Wheat requires 450-650mm of water throughout its growing season. 
Critical irrigation stages:
1. Crown Root Initiation (CRI) - 21 days after sowing
2. Tillering Stage - 40-45 days after sowing
3. Jointing Stage - 60-65 days after sowing
4. Flowering Stage - 75-80 days after sowing
5. Grain Filling Stage - 90-100 days after sowing

Total irrigations needed: 5-6 for normal soil, 4-5 for heavy soil.
Avoid waterlogging. Ensure proper drainage."""
    },
    {
        "title": "Maize Irrigation Schedule",
        "content": """Maize water requirements: 500-800mm throughout growing season.
Critical irrigation stages:
1. Pre-sowing irrigation (if soil moisture is low)
2. Knee-high stage - 2-3 weeks after sowing
3. Tasseling stage - 45-50 days after sowing
4. Silking stage - 55-60 days after sowing
5. Grain filling stage - 65-75 days after sowing

Total irrigations: 6-8 depending on rainfall and soil type.
Most critical: Tasseling to grain filling period."""
    },
    {
        "title": "Wheat Rust Disease",
        "content": """Wheat Rust (Yellow, Brown, Black rust) identification and treatment:

Symptoms:
- Orange-brown to black pustules on leaves and stems
- Yellow rust: Yellow-orange stripes on leaves
- Brown rust: Small brown pustules scattered on leaves
- Black rust: Black pustules on stems and leaf sheaths

Prevention:
- Use resistant varieties (HD-2967, PBW-343, DBW-17)
- Proper spacing for air circulation
- Remove volunteer wheat plants
- Balanced fertilization (avoid excess nitrogen)

Treatment:
- Propiconazole 25% EC @ 250ml/acre
- Tebuconazole 25.9% EC @ 200ml/acre
- Apply at first sign of disease
- Repeat after 15 days if needed"""
    },
    {
        "title": "Maize Fall Armyworm",
        "content": """Fall Armyworm (Spodoptera frugiperda) - Major maize pest:

Identification:
- Green to brown caterpillars with white inverted Y on head
- Feed on leaves, creating characteristic "window pane" damage
- Can destroy entire crop if not controlled

Prevention:
- Early sowing to avoid peak infestation
- Intercropping with pulses
- Pheromone traps for monitoring
- Remove and destroy egg masses

Treatment:
- Chlorantraniliprole 18.5% SC @ 60ml/acre
- Emamectin benzoate 5% SG @ 80g/acre
- Spray in early morning or evening
- Target whorl of plant where larvae hide
- Apply when 5% plants show damage"""
    },
    {
        "title": "Wheat NPK Fertilizer Schedule",
        "content": """Wheat fertilizer recommendations for optimal yield:

For Loamy Soil (per acre):
Basal Dose (at sowing):
- Nitrogen (N): 60 kg
- Phosphorus (P2O5): 30 kg
- Potassium (K2O): 20 kg
- Zinc Sulphate: 10 kg (if deficient)

Top Dressing:
- First: 40 kg N at Crown Root Initiation (21 days)
- Second: 20 kg N at Flowering (60-65 days)

For Heavy Soil:
- Reduce N by 20%
- Increase P by 10%

For Sandy Soil:
- Increase N by 20%
- Split N into 3 doses

Note: Apply urea after irrigation for better absorption."""
    },
    {
        "title": "Maize NPK Fertilizer Schedule",
        "content": """Maize fertilizer recommendations for maximum yield:

For Normal Soil (per acre):
Basal Dose (at sowing):
- Nitrogen (N): 50 kg
- Phosphorus (P2O5): 25 kg
- Potassium (K2O): 25 kg
- Zinc Sulphate: 10 kg

Top Dressing:
- First: 50 kg N at Knee-high stage (25-30 days)
- Second: 30 kg N at Tasseling (45-50 days)

Additional for High-Yielding Varieties:
- Add 20 kg N at silking stage

Micronutrients:
- Zinc: 10 kg/acre if deficiency symptoms
- Boron: 2 kg/acre for better grain filling

Apply fertilizer 5-7 cm away from plant base."""
    },
    {
        "title": "Wheat Sowing Guidelines",
        "content": """Optimal wheat sowing practices:

Sowing Time:
- Timely sown: November 1-15 (North India)
- Late sown: November 16 - December 15
- Very late: After December 15 (use early varieties)

Seed Rate:
- Normal conditions: 40 kg/acre
- Late sowing: 50 kg/acre
- Very late sowing: 60 kg/acre

Seed Treatment:
- Vitavax @ 2.5g/kg seed (for fungal diseases)
- Imidacloprid @ 5ml/kg seed (for termites)

Sowing Method:
- Line sowing preferred (better yield)
- Row spacing: 20-23 cm
- Seed depth: 4-5 cm
- Use seed drill for uniform sowing

Land Preparation:
- 2-3 ploughings
- Level field properly
- Apply FYM 8-10 tons/acre before last ploughing"""
    },
    {
        "title": "Maize Sowing Guidelines",
        "content": """Optimal maize sowing practices:

Sowing Time:
- Kharif (Monsoon): June-July
- Rabi (Winter): October-November
- Spring: February-March

Seed Rate:
- Normal varieties: 8 kg/acre
- Hybrid varieties: 6 kg/acre
- Sweet corn: 10 kg/acre

Spacing:
- Row to row: 60 cm
- Plant to plant: 20-25 cm
- For mechanization: 75 cm x 20 cm

Seed Treatment:
- Thiram @ 3g/kg seed
- Imidacloprid @ 5ml/kg seed

Sowing Depth:
- Normal soil: 4-5 cm
- Heavy soil: 3-4 cm
- Light soil: 5-6 cm

Land Preparation:
- Deep ploughing in summer
- 2-3 harrowings
- Level field for uniform germination
- Make ridges and furrows for better drainage"""
    },
    {
        "title": "Wheat Weed Management",
        "content": """Weed control in wheat for better yield:

Common Weeds:
- Broad-leaf: Bathua, Jangli palak, Khet papra
- Narrow-leaf: Gul danda, Jangli javi

Critical Period:
- First 30-40 days after sowing
- Maximum competition at 20-35 days

Control Methods:

1. Cultural Control:
- Use certified seed
- Proper land preparation
- Timely sowing
- Crop rotation

2. Mechanical Control:
- Hand weeding at 30-35 days
- Use wheel hoe between rows

3. Chemical Control:

For Broad-leaf weeds:
- 2,4-D @ 500ml/acre at 30-35 days
- Metsulfuron @ 8g/acre at 25-30 days

For Narrow-leaf weeds:
- Clodinafop @ 200ml/acre at 30-35 days
- Sulfosulfuron @ 100g/acre at 25-30 days

For Mixed weeds:
- Sulfosulfuron + Metsulfuron @ 120g/acre

Application: Spray when weeds are young (2-4 leaf stage)"""
    },
    {
        "title": "Soil Health Management",
        "content": """Maintaining soil health for sustainable farming:

Soil Testing:
- Test soil every 2-3 years
- Check pH, NPK, organic carbon, micronutrients
- Optimal pH for wheat/maize: 6.5-7.5

Organic Matter:
- Apply FYM/compost: 8-10 tons/acre annually
- Green manuring with dhaincha/sunhemp
- Incorporate crop residues
- Target: 1-2% organic carbon

Crop Rotation:
- Wheat-Maize-Pulses rotation
- Include legumes every 2-3 years
- Avoid monoculture

Soil Conservation:
- Contour farming on slopes
- Mulching to prevent erosion
- Maintain soil cover
- Avoid over-tillage

Micronutrient Management:
- Zinc: Apply ZnSO4 @ 10 kg/acre every 2-3 years
- Iron: Foliar spray of FeSO4 @ 0.5% if deficiency
- Boron: Apply borax @ 2 kg/acre for maize

Avoid:
- Burning crop residues
- Excessive chemical fertilizers
- Waterlogging
- Soil compaction from heavy machinery"""
    }
]

def add_document(title, content):
    """Add a document to RAG"""
    try:
        response = requests.post(
            f"{SERVER_URL}/rag/documents",
            json={"title": title, "content": content},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print(f"✅ Added: {title}")
                return True
            else:
                print(f"❌ Failed to add {title}: {data.get('error')}")
                return False
        else:
            print(f"❌ HTTP {response.status_code} for {title}")
            return False
            
    except Exception as e:
        print(f"❌ Error adding {title}: {e}")
        return False

def main():
    print("="*60)
    print("🌾 Populating RAG with Farming Knowledge")
    print("="*60)
    print()
    
    # Check if server is running
    try:
        response = requests.get(f"{SERVER_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ Server not responding. Please start the HTTP wrapper first:")
            print("   cd server")
            print("   python smart_load_balancer_http_wrapper_v4.py")
            return
    except Exception as e:
        print(f"❌ Cannot connect to server at {SERVER_URL}")
        print("   Please start the HTTP wrapper first:")
        print("   cd server")
        print("   python smart_load_balancer_http_wrapper_v4.py")
        return
    
    print(f"📡 Connected to {SERVER_URL}")
    print(f"📚 Adding {len(FARMING_DOCUMENTS)} documents...\n")
    
    success_count = 0
    for doc in FARMING_DOCUMENTS:
        if add_document(doc["title"], doc["content"]):
            success_count += 1
    
    print()
    print("="*60)
    print(f"✅ Successfully added {success_count}/{len(FARMING_DOCUMENTS)} documents")
    print("="*60)
    print()
    print("Next steps:")
    print("1. Open http://localhost:3000/smart-loadbalancer-v4")
    print("2. Connect to the server")
    print("3. Enable RAG toggle in the header")
    print("4. Ask farming questions like:")
    print("   - 'When should I irrigate wheat?'")
    print("   - 'How to control rust in wheat?'")
    print("   - 'What fertilizer for maize?'")
    print()

if __name__ == "__main__":
    main()
