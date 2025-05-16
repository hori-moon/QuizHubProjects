from .supabase_client import supabase

def insert_quiz_to_supabase(question, answer):
    data = {"content": question, "answer": answer}
    return supabase.table("questions").insert(data).execute()