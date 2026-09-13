param([string]$IndexPath)

$ErrorActionPreference = 'Stop'
$qaExpectedRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../../../output/final-word-qa-r17'))
if (-not $IndexPath) { $IndexPath = Join-Path $qaExpectedRoot 'collection-index.json' }
$qaIndexPath = [IO.Path]::GetFullPath($IndexPath)
if ((Split-Path -Parent $qaIndexPath) -ne $qaExpectedRoot) {
    throw 'Only the R17 QA collection index may be rendered by this script.'
}
$qaIndex = Get-Content -Raw -LiteralPath $qaIndexPath | ConvertFrom-Json
if ($qaIndex.stage -ne 'collected-after-parent-completion') { throw 'No completed-batch collection is bound.' }
$qaResults = [System.Collections.Generic.List[object]]::new()
$qaRootPrefix = $qaExpectedRoot.TrimEnd('\', '/') + [IO.Path]::DirectorySeparatorChar

foreach ($qaCall in $qaIndex.calls) {
    foreach ($qaArtifact in $qaCall.documents) {
        $qaInput = [IO.Path]::GetFullPath($qaArtifact.recovered)
        if (-not $qaInput.StartsWith($qaRootPrefix, [StringComparison]::OrdinalIgnoreCase)) {
            throw 'DOCX path is outside this QA collection.'
        }
        $qaDirectory = [IO.Path]::GetFullPath((Join-Path $qaExpectedRoot ('renders/' + $qaCall.id + '/' + $qaArtifact.document_id)))
        if (-not $qaDirectory.StartsWith($qaRootPrefix, [StringComparison]::OrdinalIgnoreCase)) {
            throw 'Render output is outside this QA collection.'
        }
        New-Item -ItemType Directory -Path $qaDirectory -Force | Out-Null
        $qaPdf = Join-Path $qaDirectory 'document.pdf'
        $qaWord = $null
        $qaDocument = $null
        $qaRow = [ordered]@{
            id = $qaCall.id
            document_id = $qaArtifact.document_id
            linked_from_final = $qaArtifact.linked_from_final
            renderer = 'Microsoft Word COM read-only, one instance per DOCX'
            input = $qaInput
            pdf = $qaPdf
            expected_sha256 = $qaArtifact.docx_sha256
            success = $false
        }
        try {
            $qaRow.before_sha256 = (Get-FileHash -LiteralPath $qaInput -Algorithm SHA256).Hash.ToLowerInvariant()
            if ($qaRow.before_sha256 -ne $qaArtifact.docx_sha256) { throw 'Collected DOCX changed before rendering.' }
            $qaWord = New-Object -ComObject Word.Application
            $qaWord.Visible = $false
            $qaWord.DisplayAlerts = 0
            $qaWord.AutomationSecurity = 3
            $qaRow.word_version = $qaWord.Version
            $qaDocument = $qaWord.Documents.Open($qaInput, $false, $true, $false)
            $qaRow.read_only = $qaDocument.ReadOnly
            if (-not $qaDocument.ReadOnly) { throw 'Word did not open this DOCX read-only.' }
            $qaRow.pages = $qaDocument.ComputeStatistics(2)
            $qaRow.word_text = $qaDocument.Content.Text
            $qaDocument.ExportAsFixedFormat($qaPdf, 17)
            $qaRow.success = (Test-Path -LiteralPath $qaPdf) -and (Get-Item -LiteralPath $qaPdf).Length -gt 0
        } catch {
            $qaRow.error = $_.Exception.Message
        } finally {
            if ($null -ne $qaDocument) {
                try { $qaDocument.Close(0) } catch { $qaRow.close_error = $_.Exception.Message }
                [void][Runtime.InteropServices.Marshal]::ReleaseComObject($qaDocument)
            }
            if ($null -ne $qaWord) {
                try { $qaWord.Quit(0) } catch { $qaRow.quit_error = $_.Exception.Message }
                [void][Runtime.InteropServices.Marshal]::ReleaseComObject($qaWord)
            }
        }
        if (Test-Path -LiteralPath $qaInput) {
            $qaRow.after_sha256 = (Get-FileHash -LiteralPath $qaInput -Algorithm SHA256).Hash.ToLowerInvariant()
            $qaRow.input_unchanged = $qaRow.after_sha256 -eq $qaRow.expected_sha256
            if (-not $qaRow.input_unchanged) { $qaRow.success = $false }
        }
        $qaResults.Add([pscustomobject]$qaRow)
        $qaResults | ConvertTo-Json -Depth 7 | Set-Content -LiteralPath (Join-Path $qaExpectedRoot 'word-render-results.json') -Encoding utf8
        Write-Output ($qaCall.id + '/' + $qaArtifact.document_id + ': success=' + $qaRow.success + ', pages=' + $qaRow.pages)
    }
}
