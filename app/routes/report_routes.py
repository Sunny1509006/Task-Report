from fastapi import APIRouter, Depends, Query, HTTPException
from datetime import datetime, timedelta
from app.utils.reports import generate_weekly_report
from app.dependencies import get_current_user

router = APIRouter()

@router.post("/reports/manual", summary="Generate manual report for last 7 days")
async def manual_report_generation(current_user=Depends(get_current_user)):
    user_id = current_user.get("sub")
    if not user_id:
        return {"error": "User ID not found in token"}

    today = datetime.utcnow().date()
    start_date = today - timedelta(days=7)
    end_date = today - timedelta(days=1)

    report = await generate_weekly_report(user_id, start_date, end_date)

    return {
        "message": "Report generated successfully",
        "start_date": str(start_date),
        "end_date": str(end_date),
        "report_html": report["report_html"]
    }

@router.get("/reports/weekly", summary="Generate weekly report with custom date range")
async def weekly_report(
    start_date: str = Query(..., description="Start date in YYYY-MM-DD"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD"),
    current_user=Depends(get_current_user)
):
    user_id = current_user.get("sub")
    if not user_id:
        return {"error": "User ID not found in token"}

    try:
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format, use YYYY-MM-DD")

    if start_date_obj > end_date_obj:
        raise HTTPException(status_code=400, detail="start_date cannot be after end_date")

    report = await generate_weekly_report(user_id, start_date_obj, end_date_obj)

    return {
        "message": "Report generated successfully",
        "start_date": str(start_date_obj),
        "end_date": str(end_date_obj),
        "report_html": report["report_html"]
    }
