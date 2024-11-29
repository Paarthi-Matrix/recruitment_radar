from supabase import create_client, Client
import pandas as pd


url = "https://eyrfzesoxcmvrrmpgwqp.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV5cmZ6ZXNveGNtdnJybXBnd3FwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzI3MDYwNDYsImV4cCI6MjA0ODI4MjA0Nn0.AqE7eVo3ShVA6ed_egkooKRtMmapWYUqH8ZX5X97lVI"

# Create a Supabase client
supabase: Client = create_client(url, key)

# Example: Fetch data from a table
users = supabase.table('users').select('*').execute()
candidate_factors = supabase.table('candidate_factors').select('*').execute()
company_factors = supabase.table('company_factors').select('*').execute()

# users = pd.DataFrame(users)

# Print fetched data
print(candidate_factors)