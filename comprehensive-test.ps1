Write-Host "=== Medical Coding API Comprehensive Test ===" -ForegroundColor Magenta

$baseUrl = "http://localhost:8000"

function Test-Endpoint {
    param($Name, $Url, $Method = "Get", $Body = $null)
    
    try {
        Write-Host "`nTesting $Name..." -ForegroundColor Yellow
        if ($Body) {
            $result = Invoke-RestMethod -Uri $Url -Method $Method -Body $Body -ContentType "application/json"
        } else {
            $result = Invoke-RestMethod -Uri $Url -Method $Method
        }
        Write-Host "✓ SUCCESS: $Name" -ForegroundColor Green
        return $result
    }
    catch {
        Write-Host "✗ FAILED: $Name - $($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

# Test basic endpoints
Test-Endpoint -Name "Health Check" -Url "$baseUrl/health"
Test-Endpoint -Name "Root Endpoint" -Url "$baseUrl/"
Test-Endpoint -Name "API Info" -Url "$baseUrl/info"

# Test medical coding analysis with different cases
$testCases = @(
    @{
        name = "Appendicitis Case"
        description = "Patient with acute RLQ pain, nausea, fever. Suspected appendicitis. Plan for laparoscopic appendectomy."
    },
    @{
        name = "Diabetes Follow-up"
        description = "55-year-old female with type 2 diabetes for routine follow-up. HbA1c 7.2%. Adjusting metformin dosage."
    },
    @{
        name = "Hypertension Management"
        description = "68-year-old male with essential hypertension. Blood pressure 145/88. Medication review and adjustment."
    }
)

foreach ($case in $testCases) {
    $body = @{
        patient_description = $case.description
        max_cpt_codes = 4
        max_icd_codes = 4
        max_hcpcs_codes = 2
    } | ConvertTo-Json
    
    $result = Test-Endpoint -Name $case.name -Url "$baseUrl/analyze" -Method "Post" -Body $body
    
    if ($result) {
        Write-Host "  Report ID: $($result.report_id)" -ForegroundColor Cyan
        Write-Host "  Codes Found: $($result.raw_agent_output.cpt_codes.Count) CPT, $($result.raw_agent_output.icd10_codes.Count) ICD-10" -ForegroundColor White
    }
}

Write-Host "`n🎉 All tests completed!" -ForegroundColor Green
Write-Host "`n📚 Interactive Documentation: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "🩺 Health Check: http://localhost:8000/health" -ForegroundColor Cyan
Write-Host "⚡ API Info: http://localhost:8000/info" -ForegroundColor Cyan
