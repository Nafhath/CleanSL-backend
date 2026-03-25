from app.core.supabase_client import supabase
from datetime import datetime, timezone

def generate_anomalies():
    response = supabase.table("addresses").select("*").execute()
    addresses = response.data or []

    results = []
    
    for raw_house in addresses:
        if not isinstance(raw_house, dict):
            continue

        try:
            house_id = raw_house.get("id")
            street = raw_house.get("street_address", "Unknown")
            violations = raw_house.get("violation_count", 0)
            last_collection_str = raw_house.get("last_collection_at")
            
            if not last_collection_str:
                continue

            last_collection_at = datetime.fromisoformat(last_collection_str.replace('Z', '+00:00'))
            days_since = (datetime.now(timezone.utc) - last_collection_at).days

            comp_res = supabase.table("complaints") \
                .select("id", count="exact") \
                .eq("address_id", house_id) \
                .eq("status", "pending") \
                .execute()
            
            complaint_count = comp_res.count or 0
            has_complaint = complaint_count > 0

            score = (int(days_since) * 2) + (int(violations) * 5) + (int(complaint_count) * 10)
            
            status = "NEUTRAL"
            if days_since >= 14 and has_complaint and violations > 3:
                status = "RED"
            elif (has_complaint and violations > 3) or (days_since >= 14 and has_complaint):
                status = "YELLOW"
            elif days_since <= 7:
                status = "GREEN"

            # Map to Violations.jsx format
            mapped_status = "Resolved"
            if status == "RED": mapped_status = "Confirmed"
            elif status == "YELLOW": mapped_status = "Pending"
            
            # Filter out non-anomalies
            if status != "NEUTRAL":
                results.append({
                    "date": datetime.now().strftime("%d/%m/%Y"),
                    "type": f"AI Flag ({status})",
                    "resident": street,
                    "status": mapped_status,
                    "score": min(score, 100) # Cap at 100 for gauge UI
                })

        except Exception as e:
            print("Error processing anomaly:", e)
            continue
    
    results.sort(key=lambda x: x['score'], reverse=True)
    return results
