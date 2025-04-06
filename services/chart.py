from typing import Dict, Optional
from datetime import datetime
from models import BirthData
from services.planetary import calculate_kundali, calculate_transits
from services.divisional_charts import (
    calculate_hora, calculate_drekkana, calculate_saptamsa,
    calculate_navamsa, calculate_dwadasamsa, calculate_trimsamsa
)
from services.dasha import calculate_vimshottari_dasha
from services.bala import calculate_sthana_bala, calculate_dig_bala
from db import save_chart
from fastapi import HTTPException
from utils import sanitize_birth_data

def generate_chart(data: BirthData, tz_offset: float, transit_date: Optional[datetime], 
                   ayanamsa_type: Optional[str], user_id: Optional[int], db) -> Dict:
    """
    Generate a complete astrological chart with kundali, divisional charts, dasha, transits, and bala.
    """
    try:
        sanitized_data = sanitize_birth_data(data, tz_offset)

        # Handle optional transit_date
        if transit_date is not None and (transit_date.year < 1 or transit_date.year > 9999):
            raise ValueError("Transit date year must be between 1 and 9999")
        
        # Calculate all components
        kundali = calculate_kundali(sanitized_data, tz_offset, ayanamsa_type)
        D2_hora = calculate_hora(kundali)
        D3_drekkana = calculate_drekkana(kundali)
        D7_saptamsa = calculate_saptamsa(kundali)
        D9_navamsa = calculate_navamsa(kundali)
        D12_dwadasamsa = calculate_dwadasamsa(kundali)
        D30_trimsamsa = calculate_trimsamsa(kundali)
        dasha = calculate_vimshottari_dasha(sanitized_data, kundali["planets"]["Moon"])
        transits = calculate_transits(sanitized_data, tz_offset, transit_date, ayanamsa_type)
        sthana_bala = calculate_sthana_bala(kundali, D2_hora, D3_drekkana, D7_saptamsa, 
                                            D9_navamsa, D12_dwadasamsa, D30_trimsamsa)
        dig_bala = calculate_dig_bala(kundali)

        # Prepare birth data for storage
        birth_data = sanitized_data.dict()
        birth_data["tz_offset"] = tz_offset
        birth_data["ayanamsa_type"] = ayanamsa_type

        # Structure the result
        result = {
            "kundali": kundali,
            "vimshottari_dasha": dasha,
            "transits": transits,
            "vargas": {
                "D-2": D2_hora,
                "D-3": D3_drekkana,
                "D-7": D7_saptamsa,
                "D-9": D9_navamsa,
                "D-12": D12_dwadasamsa,
                "D-30": D30_trimsamsa
            },
            "sthana_bala": sthana_bala,
            "dig_bala": dig_bala
        }

        # Save to database and attach chart_id and user_id
        chart_id = save_chart(birth_data, result, user_id, db)
        result["chart_id"] = chart_id
        result["user_id"] = user_id

        return result
    except ValueError as e:
        raise ValueError(f"Chart generation failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error in chart generation: {str(e)}")