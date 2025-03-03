from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
import sqlite3
import pandas as pd
from langchain_openai import ChatOpenAI
from .prompts import schema_description, sql_prompt, answer_prompt, query_summarization_prompt
from langchain.memory import ConversationSummaryMemory
from supplychain.models import PredictionsUtilization, Order
from sqlalchemy import create_engine
from collections import defaultdict
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
import os
from dotenv import load_dotenv

load_dotenv()

# Database (Run it once just to create the database when importing the data)

queryset = PredictionsUtilization.objects.all().values()
df = pd.DataFrame(queryset)

engine = create_engine("sqlite:///db.sqlite3")

df.to_sql("supply_chain", engine, index=False, if_exists="replace")

# pre-processing user questions
llm_summary = ChatOpenAI(
    model_name="o3-mini",
    openai_api_key=os.getenv("OPENAI_API_KEY")
)


llm = ChatOpenAI(
    model_name="gpt-4o-mini", 
    temperature=0.7, 
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

memory = ConversationSummaryMemory(llm=llm, memory_key="chat_history", return_messages=True)

def home_view(request):
    return render(request, "home.html")

def execute_sql_query(query):
    try:
        conn = sqlite3.connect("db.sqlite3", check_same_thread=False)
        result_df = pd.read_sql_query(query, conn)
        conn.close()

        if result_df.empty:
            return "No relevant data found."
        return result_df.to_string(index=False)
    except Exception as e:
        return f"SQL Error: {e}"


def home_view(request):
    return render(request, "home.html")

def chatbot_query(request):
    if request.method == "POST":
        user_input = request.POST.get("question", "").strip()

        if not user_input:
            return JsonResponse({"error": "Question is required"}, status=400)

        chat_history = memory.load_memory_variables({}).get("chat_history", [])

        summarized_intent = llm_summary.invoke(
            query_summarization_prompt.format(
                chat_history=chat_history, new_question=user_input
            )
        ).content.strip()

        print("\nSummarized User Intent:", summarized_intent)

        generated_sql = llm.invoke(sql_prompt.format(schema=schema_description, question=summarized_intent)).content.strip()

        print("\nGenerated SQL Query:", generated_sql)

        query_result = execute_sql_query(generated_sql)

        print("\nQuery Result:", query_result)

        final_answer = llm.invoke(answer_prompt.format(question=summarized_intent, query_result=query_result)).content.strip()

        print("\nAI Response:", final_answer)

        memory.save_context({"question": user_input}, {"answer": final_answer})

        return JsonResponse({"answer": final_answer})

    return JsonResponse({"error": "Invalid request"}, status=400)


def alerts_view(request):
    alerts = PredictionsUtilization.objects.filter(increase_capacity="Yes", ordered=False)

    alerts_by_city = defaultdict(list)
    for alert in alerts:
        remaining_capacity = alert.existing_capacity - alert.units_increase
        alerts_by_city[alert.location].append({
            "id": alert.id,
            "date": alert.date,
            "predicted_demand": alert.predicted_demand,
            "existing_capacity": alert.existing_capacity,
            "units_increase": alert.units_increase,
            "remaining_capacity": remaining_capacity,
            "supplier_chosen": alert.supplier_chosen or "N/A",
            "order_cost": alert.order_cost,
        })

    old_alerts = PredictionsUtilization.objects.filter(ordered=True)

    old_alerts_data = []
    for old_alert in old_alerts:
        old_alerts_data.append({
            "id": old_alert.id,
            "date": old_alert.date,
            "location": old_alert.location,
            "existing_capacity": old_alert.existing_capacity,
            "units_increase": old_alert.units_increase,
            "order_cost": old_alert.order_cost,
            "supplier_chosen": old_alert.supplier_chosen or "N/A",
        })

    return render(request, "alerts.html", {
        "alerts_by_city": dict(alerts_by_city),
        "old_alerts": old_alerts_data,
    })


def accept_order(request, alert_id):
    if request.method == "POST":
        alert = get_object_or_404(PredictionsUtilization, id=alert_id)

        if not alert.ordered:
            alert.ordered = True
            alert.save()

            Order.objects.create(
                location=alert.location,
                date=alert.date,
                units_increase=alert.units_increase,
                supplier_chosen=alert.supplier_chosen,
                order_cost=alert.order_cost
            )

        return redirect("supplychain:alerts")

    return redirect("supplychain:alerts")


def generate_report(request, prediction_id):

    alert = PredictionsUtilization.objects.get(id=prediction_id)

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    margin = 50
    max_width = width - 2 * margin

    c.setFont("Helvetica-Bold", 18)
    title = "CONFIDENTIAL: Executive Capacity Increase Report"
    title_width = c.stringWidth(title, "Helvetica-Bold", 18)
    c.drawString((width - title_width) / 2, height - 50, title)

    y_position = height - 90
    c.setFont("Helvetica", 12)

    text = (
        "To: Executive Leadership Team\n\n"
        "Subject: Strategic Capacity Expansion Initiative\n\n"
        "Dear Executive Team,\n\n"
        "Following a comprehensive analysis of demand projections, we have identified an essential capacity expansion "
        "requirement at the following location:\n\n"
        "Location: {location}\n"
        "Date of Implementation: {date}\n"
        "Proposed Units Increase: {units_increase}\n"
        "Preferred Supplier: {supplier_chosen}\n"
        "Projected Investment: ${order_cost:,d}\n\n"
        "This strategic investment aligns with our growth objectives and ensures operational efficiency to meet anticipated "
        "market demand. We recommend proceeding with the supplier engagement and procurement process immediately.\n\n"
        "For further discussions or approvals, please advise on the next steps.\n\n"
        "Best regards,\n"
        "Operations Strategy Division"
    ).format(
        location=alert.location,
        date=alert.date.strftime("%Y-%m-%d"),
        units_increase=alert.units_increase,
        supplier_chosen=alert.supplier_chosen or "N/A",
        order_cost=int(alert.order_cost)
    )

    for line in text.split("\n"):
        if c.stringWidth(line, "Helvetica", 12) > max_width:
            words = line.split()
            new_line = ""
            for word in words:
                if c.stringWidth(new_line + " " + word, "Helvetica", 12) < max_width:
                    new_line += " " + word
                else:
                    c.drawString(margin, y_position, new_line.strip())
                    y_position -= 15
                    new_line = word
            c.drawString(margin, y_position, new_line.strip())
        else:
            c.drawString(margin, y_position, line)
        y_position -= 15

    c.save()
    buffer.seek(0)
    
    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="Increase_{alert.location}_{alert.date}.pdf"'
    return response


def past_orders_view(request):
    past_orders = Order.objects.all().order_by("-date")

    orders_by_supplier = defaultdict(list)
    for order in past_orders:
        supplier_name = order.supplier_chosen
        orders_by_supplier[supplier_name].append(order)

    return render(request, "orders.html", {
        "orders_by_supplier": dict(orders_by_supplier),
    })