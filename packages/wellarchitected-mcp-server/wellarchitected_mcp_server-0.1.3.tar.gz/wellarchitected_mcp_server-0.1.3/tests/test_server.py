"""Tests for the Well-Architected MCP server"""

import pytest
from unittest.mock import patch, MagicMock
from wellarchitected_mcp_server.server import (
    list_lenses,
    list_workloads,
    get_workload_details,
    create_workload,
    list_answers
)


class TestWellArchitectedMCPServer:
    """Test suite for Well-Architected MCP server functions"""

    @patch('wellarchitected_mcp_server.server.wellarchitected_client')
    def test_list_lenses(self, mock_client):
        """Test listing lenses"""
        # Mock response
        mock_client.list_lenses.return_value = {
            "LensSummaries": [
                {
                    "LensAlias": "wellarchitected",
                    "LensName": "AWS Well-Architected Framework",
                    "LensVersion": "2020-07-02",
                    "Description": "AWS Well-Architected Framework"
                }
            ]
        }
        
        result = list_lenses()
        
        assert len(result) == 1
        assert result[0]["LensAlias"] == "wellarchitected"
        mock_client.list_lenses.assert_called_once_with(MaxResults=50)

    @patch('wellarchitected_mcp_server.server.wellarchitected_client')
    def test_list_workloads(self, mock_client):
        """Test listing workloads"""
        # Mock response
        mock_client.list_workloads.return_value = {
            "WorkloadSummaries": [
                {
                    "WorkloadId": "test-workload-id",
                    "WorkloadName": "Test Workload",
                    "Environment": "PRODUCTION"
                }
            ]
        }
        
        result = list_workloads()
        
        assert len(result) == 1
        assert result[0]["WorkloadId"] == "test-workload-id"
        mock_client.list_workloads.assert_called_once_with(MaxResults=50)

    @patch('wellarchitected_mcp_server.server.wellarchitected_client')
    def test_get_workload_details(self, mock_client):
        """Test getting workload details"""
        # Mock response
        mock_client.get_workload.return_value = {
            "Workload": {
                "WorkloadId": "test-workload-id",
                "WorkloadName": "Test Workload",
                "Description": "Test workload description"
            }
        }
        
        result = get_workload_details("test-workload-id")
        
        assert result["WorkloadId"] == "test-workload-id"
        mock_client.get_workload.assert_called_once_with(WorkloadId="test-workload-id")

    @patch('wellarchitected_mcp_server.server.wellarchitected_client')
    def test_create_workload(self, mock_client):
        """Test creating a workload"""
        # Mock response
        mock_client.create_workload.return_value = {
            "WorkloadId": "new-workload-id",
            "WorkloadArn": "arn:aws:wellarchitected:us-east-1:123456789012:workload/new-workload-id"
        }
        
        result = create_workload(
            workload_name="Test Workload",
            description="Test description",
            environment="PRODUCTION",
            aws_regions=["us-east-1"]
        )
        
        assert result["WorkloadId"] == "new-workload-id"
        assert "WorkloadArn" in result
        mock_client.create_workload.assert_called_once()

    @patch('wellarchitected_mcp_server.server.wellarchitected_client')
    def test_list_answers(self, mock_client):
        """Test listing answers"""
        # Mock response
        mock_client.list_answers.return_value = {
            "AnswerSummaries": [
                {
                    "QuestionId": "test-question-id",
                    "PillarId": "security",
                    "QuestionTitle": "Test Question",
                    "Risk": "MEDIUM"
                }
            ]
        }
        
        result = list_answers("test-workload-id")
        
        assert len(result) == 1
        assert result[0]["QuestionId"] == "test-question-id"
        mock_client.list_answers.assert_called_once_with(
            WorkloadId="test-workload-id",
            LensAlias="wellarchitected"
        )

    @patch('wellarchitected_mcp_server.server.wellarchitected_client')
    def test_error_handling(self, mock_client):
        """Test error handling"""
        from botocore.exceptions import ClientError
        
        # Mock a client error
        mock_client.list_lenses.side_effect = ClientError(
            error_response={
                'Error': {
                    'Code': 'AccessDenied',
                    'Message': 'Access denied'
                }
            },
            operation_name='ListLenses'
        )
        
        result = list_lenses()
        
        assert "error" in result
        assert "AccessDenied" in result["error"]
