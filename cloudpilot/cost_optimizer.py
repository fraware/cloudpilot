from __future__ import annotations

import logging

import boto3

from cloudpilot.config import load_settings

logger = logging.getLogger(__name__)


def get_aws_cost_optimization(current_instance_type: str) -> str:
    """
    Query AWS Pricing API for the instance type and return a short recommendation.
    """
    region = load_settings().aws_pricing_region
    try:
        pricing = boto3.client("pricing", region_name=region)
        pricing.get_products(
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
        return (
            f"Retrieved pricing data for {current_instance_type}. "
            f"Consider comparing with alternatives (e.g., m5.large) for cost savings."
        )
    except Exception as e:
        logger.debug("AWS pricing error: %s", e)
        return f"Error retrieving pricing data: {str(e)}"
