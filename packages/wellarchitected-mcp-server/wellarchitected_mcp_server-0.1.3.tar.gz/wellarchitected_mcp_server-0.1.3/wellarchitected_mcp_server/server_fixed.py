#!/usr/bin/env python3
"""
AWS Well-Architected MCP Server

This server provides tools to interact with AWS Well-Architected Framework
through the Model Context Protocol (MCP).
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from fastmcp import FastMCP
import typer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = FastMCP("aws.wellarchitected")

# AWS Configuration
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_PROFILE = os.getenv("AWS_PROFILE", "default")

try:
    # Initialize AWS session
    session = boto3.Session(profile_name=AWS_PROFILE, region_name=AWS_REGION)
    wellarchitected_client = session.client("wellarchitected")
    
    # Test AWS connection
    wellarchitected_client.list_lenses(MaxResults=1)
    logger.info(f"Successfully connected to AWS Well-Architected in {AWS_REGION}")
    
except (NoCredentialsError, ClientError) as e:
    logger.error(f"AWS connection failed: {e}")
    logger.info("Please ensure AWS credentials are configured properly")

@mcp.tool()
def list_lenses(max_results: int = 50) -> List[Dict[str, Any]]:
    """
    List AWS Well-Architected lenses available in your account.
    
    Args:
        max_results: Maximum number of lenses to return (default: 50, max: 50)
    
    Returns:
        List of lens summaries with details like name, version, and description
    """
    try:
        response = wellarchitected_client.list_lenses(MaxResults=min(max_results, 50))
        return response.get("LensSummaries", [])
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        logger.error(f"AWS Error in list_lenses - {error_code}: {error_message}")
        return {"error": f"AWS Error {error_code}: {error_message}"}
    except Exception as e:
        logger.error(f"Unexpected error in list_lenses: {str(e)}")
        return {"error": f"Unexpected error: {str(e)}"}

@mcp.tool()
def get_lens_details(lens_alias: str, lens_version: Optional[str] = None) -> Dict[str, Any]:
    """
    Get detailed information about a specific Well-Architected lens.
    
    Args:
        lens_alias: The alias of the lens (e.g., 'wellarchitected')
        lens_version: Specific version of the lens (optional, uses latest if not specified)
    
    Returns:
        Detailed lens information including pillars and questions
    """
    try:
        params = {"LensAlias": lens_alias}
        if lens_version:
            params["LensVersion"] = lens_version
        response = wellarchitected_client.get_lens(**params)
        return response.get("Lens", {})
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        logger.error(f"AWS Error in get_lens_details - {error_code}: {error_message}")
        return {"error": f"AWS Error {error_code}: {error_message}"}
    except Exception as e:
        logger.error(f"Unexpected error in get_lens_details: {str(e)}")
        return {"error": f"Unexpected error: {str(e)}"}

@mcp.tool()
def list_workloads(max_results: int = 50) -> List[Dict[str, Any]]:
    """
    List AWS Well-Architected workloads in your account.
    
    Args:
        max_results: Maximum number of workloads to return (default: 50, max: 50)
    
    Returns:
        List of workload summaries with basic information
    """
    try:
        response = wellarchitected_client.list_workloads(MaxResults=min(max_results, 50))
        return response.get("WorkloadSummaries", [])
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        logger.error(f"AWS Error in list_workloads - {error_code}: {error_message}")
        return {"error": f"AWS Error {error_code}: {error_message}"}
    except Exception as e:
        logger.error(f"Unexpected error in list_workloads: {str(e)}")
        return {"error": f"Unexpected error: {str(e)}"}

@mcp.tool()
def get_workload_details(workload_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific workload.
    
    Args:
        workload_id: The ID of the workload
    
    Returns:
        Detailed workload information including architecture and review details
    """
    try:
        response = wellarchitected_client.get_workload(WorkloadId=workload_id)
        return response.get("Workload", {})
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        logger.error(f"AWS Error in get_workload_details - {error_code}: {error_message}")
        return {"error": f"AWS Error {error_code}: {error_message}"}
    except Exception as e:
        logger.error(f"Unexpected error in get_workload_details: {str(e)}")
        return {"error": f"Unexpected error: {str(e)}"}

@mcp.tool()
def create_workload(
    workload_name: str,
    description: str,
    environment: str,
    aws_regions: List[str],
    lenses: Optional[List[str]] = None,
    industry_type: Optional[str] = None,
    industry: Optional[str] = None,
    architecture_url: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new Well-Architected workload.
    
    Args:
        workload_name: Name of the workload
        description: Description of the workload
        environment: Environment type (PRODUCTION, PREPRODUCTION)
        aws_regions: List of AWS regions the workload uses
        lenses: List of lens aliases to apply (optional)
        industry_type: Type of industry (optional)
        industry: Specific industry (optional)
        architecture_url: URL to architecture diagram (optional)
    
    Returns:
        Created workload information including workload ID
    """
    try:
        params = {
            "WorkloadName": workload_name,
            "Description": description,
            "Environment": environment,
            "AwsRegions": aws_regions
        }
        
        if lenses:
            params["Lenses"] = lenses
        if industry_type:
            params["IndustryType"] = industry_type
        if industry:
            params["Industry"] = industry
        if architecture_url:
            params["ArchitectureUrl"] = architecture_url
        
        response = wellarchitected_client.create_workload(**params)
        return {
            "WorkloadId": response.get("WorkloadId"),
            "WorkloadArn": response.get("WorkloadArn")
        }
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        logger.error(f"AWS Error in create_workload - {error_code}: {error_message}")
        return {"error": f"AWS Error {error_code}: {error_message}"}
    except Exception as e:
        logger.error(f"Unexpected error in create_workload: {str(e)}")
        return {"error": f"Unexpected error: {str(e)}"}

@mcp.tool()
def list_answers(workload_id: str, lens_alias: str = "wellarchitected") -> List[Dict[str, Any]]:
    """
    List answers for a workload's lens review.
    
    Args:
        workload_id: The ID of the workload
        lens_alias: The alias of the lens (default: 'wellarchitected')
    
    Returns:
        List of answers with question IDs, risk levels, and notes
    """
    try:
        response = wellarchitected_client.list_answers(
            WorkloadId=workload_id,
            LensAlias=lens_alias
        )
        return response.get("AnswerSummaries", [])
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        logger.error(f"AWS Error in list_answers - {error_code}: {error_message}")
        return {"error": f"AWS Error {error_code}: {error_message}"}
    except Exception as e:
        logger.error(f"Unexpected error in list_answers: {str(e)}")
        return {"error": f"Unexpected error: {str(e)}"}

@mcp.tool()
def get_answer_details(workload_id: str, lens_alias: str, question_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific answer.
    
    Args:
        workload_id: The ID of the workload
        lens_alias: The alias of the lens
        question_id: The ID of the question
    
    Returns:
        Detailed answer information including choices, risk, and improvement plan
    """
    try:
        response = wellarchitected_client.get_answer(
            WorkloadId=workload_id,
            LensAlias=lens_alias,
            QuestionId=question_id
        )
        return response.get("Answer", {})
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        logger.error(f"AWS Error in get_answer_details - {error_code}: {error_message}")
        return {"error": f"AWS Error {error_code}: {error_message}"}
    except Exception as e:
        logger.error(f"Unexpected error in get_answer_details: {str(e)}")
        return {"error": f"Unexpected error: {str(e)}"}

@mcp.tool()
def list_milestones(workload_id: str) -> List[Dict[str, Any]]:
    """
    List milestones for a workload.
    
    Args:
        workload_id: The ID of the workload
    
    Returns:
        List of milestone summaries with dates and improvement status
    """
    try:
        response = wellarchitected_client.list_milestones(WorkloadId=workload_id)
        return response.get("MilestoneSummaries", [])
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        logger.error(f"AWS Error in list_milestones - {error_code}: {error_message}")
        return {"error": f"AWS Error {error_code}: {error_message}"}
    except Exception as e:
        logger.error(f"Unexpected error in list_milestones: {str(e)}")
        return {"error": f"Unexpected error: {str(e)}"}

@mcp.tool()
def get_lens_review_report(workload_id: str, lens_alias: str = "wellarchitected") -> str:
    """
    Get a lens review report URL for download.
    
    Args:
        workload_id: The ID of the workload
        lens_alias: The alias of the lens (default: 'wellarchitected')
    
    Returns:
        Pre-signed URL for downloading the lens review report
    """
    try:
        response = wellarchitected_client.get_lens_review_report(
            WorkloadId=workload_id,
            LensAlias=lens_alias
        )
        return response.get("LensReviewReport", {}).get("LensReviewReportUrl", "")
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        logger.error(f"AWS Error in get_lens_review_report - {error_code}: {error_message}")
        return {"error": f"AWS Error {error_code}: {error_message}"}
    except Exception as e:
        logger.error(f"Unexpected error in get_lens_review_report: {str(e)}")
        return {"error": f"Unexpected error: {str(e)}"}

@mcp.tool()
def list_improvement_summaries(workload_id: str, lens_alias: str = "wellarchitected") -> List[Dict[str, Any]]:
    """
    List improvement summaries for a workload.
    
    Args:
        workload_id: The ID of the workload
        lens_alias: The alias of the lens (default: 'wellarchitected')
    
    Returns:
        List of improvement summaries with risk levels and pillar information
    """
    try:
        response = wellarchitected_client.list_lens_review_improvements(
            WorkloadId=workload_id,
            LensAlias=lens_alias
        )
        return response.get("ImprovementSummaries", [])
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        logger.error(f"AWS Error in list_improvement_summaries - {error_code}: {error_message}")
        return {"error": f"AWS Error {error_code}: {error_message}"}
    except Exception as e:
        logger.error(f"Unexpected error in list_improvement_summaries: {str(e)}")
        return {"error": f"Unexpected error: {str(e)}"}

def main():
    """Main entry point for the CLI"""
    typer_app = typer.Typer()
    
    @typer_app.command()
    def start_server(
        host: str = typer.Option("0.0.0.0", help="Host to bind the server"),
        port: int = typer.Option(8000, help="Port to bind the server"),
        log_level: str = typer.Option("INFO", help="Logging level")
    ):
        """Start the AWS Well-Architected MCP server"""
        logging.getLogger().setLevel(getattr(logging, log_level.upper()))
        logger.info(f"Starting AWS Well-Architected MCP server on {host}:{port}")
        logger.info(f"Using AWS Profile: {AWS_PROFILE}, Region: {AWS_REGION}")
        mcp.run(host=host, port=port)
    
    @typer_app.command()
    def test_connection():
        """Test AWS connection and list available lenses"""
        try:
            response = wellarchitected_client.list_lenses(MaxResults=5)
            result = response.get("LensSummaries", [])
            
            typer.echo("✅ AWS Well-Architected connection successful!")
            typer.echo(f"📍 Region: {AWS_REGION}")
            typer.echo(f"👤 Profile: {AWS_PROFILE}")
            typer.echo(f"🔍 Available lenses: {len(result)}")
            
            for lens in result[:3]:
                typer.echo(f"  - {lens.get('LensName', 'Unknown')} ({lens.get('LensAlias', 'N/A')})")
                
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            typer.echo(f"❌ AWS connection failed: {error_code} - {error_message}")
            raise typer.Exit(1)
        except Exception as e:
            typer.echo(f"❌ Connection test failed: {e}")
            raise typer.Exit(1)
    
    typer_app()

if __name__ == "__main__":
    main()
