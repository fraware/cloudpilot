import boto3


def get_aws_cost_optimization(current_instance_type):
    """
    Retrieves pricing data for the current AWS instance type and provides
    a simple recommendation for cost optimization.

    For MVP:
      - Query AWS Pricing API for current instance pricing in US East (N. Virginia).
      - Suggest comparing against baseline instance types.
    """
    try:
        pricing = boto3.client("pricing", region_name="us-east-1")
        response = pricing.get_products(
            ServiceCode="AmazonEC2",
            Filters=[
                {
                    "Type": "TERM_MATCH",
                    "Field": "instanceType",
                    "Value": current_instance_type,
                },
                {
                    "Type": "TERM_MATCH",
                    "Field": "location",
                    "Value": "US East (N. Virginia)",
                },
                {"Type": "TERM_MATCH", "Field": "operatingSystem", "Value": "Linux"},
                {"Type": "TERM_MATCH", "Field": "preInstalledSw", "Value": "NA"},
                {"Type": "TERM_MATCH", "Field": "tenancy", "Value": "Shared"},
                {"Type": "TERM_MATCH", "Field": "capacitystatus", "Value": "Used"},
            ],
            MaxResults=1,
        )
        # Note: For a production system, you would parse response['PriceList'] (a JSON string)
        # to extract the actual hourly price. Here we simply notify the user that data was retrieved.
        recommendation = (
            f"Retrieved pricing data for {current_instance_type}. "
            f"Consider comparing with alternatives (e.g., m5.large) for cost savings."
        )
        return recommendation
    except Exception as e:
        return f"Error retrieving pricing data: {str(e)}"
