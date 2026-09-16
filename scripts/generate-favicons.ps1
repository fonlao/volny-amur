param(
    [string]$OutputDirectory = (Join-Path $PSScriptRoot '..\public')
)

Add-Type -AssemblyName System.Drawing

$resolvedOutput = [System.IO.Path]::GetFullPath($OutputDirectory)
[System.IO.Directory]::CreateDirectory($resolvedOutput) | Out-Null

function New-RoundedRectanglePath {
    param(
        [System.Drawing.RectangleF]$Rectangle,
        [float]$Radius
    )

    $diameter = $Radius * 2
    $path = [System.Drawing.Drawing2D.GraphicsPath]::new()
    $path.AddArc($Rectangle.X, $Rectangle.Y, $diameter, $diameter, 180, 90)
    $path.AddArc($Rectangle.Right - $diameter, $Rectangle.Y, $diameter, $diameter, 270, 90)
    $path.AddArc($Rectangle.Right - $diameter, $Rectangle.Bottom - $diameter, $diameter, $diameter, 0, 90)
    $path.AddArc($Rectangle.X, $Rectangle.Bottom - $diameter, $diameter, $diameter, 90, 90)
    $path.CloseFigure()
    return $path
}

function New-BrandIcon {
    param([int]$Size)

    $bitmap = [System.Drawing.Bitmap]::new($Size, $Size, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    $graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $graphics.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
    $graphics.Clear([System.Drawing.Color]::Transparent)

    $scale = $Size / 64.0
    $background = New-RoundedRectanglePath -Rectangle ([System.Drawing.RectangleF]::new(0, 0, $Size, $Size)) -Radius (15 * $scale)
    $graphics.FillPath([System.Drawing.SolidBrush]::new([System.Drawing.ColorTranslator]::FromHtml('#102C24')), $background)

    $graphics.FillEllipse(
        [System.Drawing.SolidBrush]::new([System.Drawing.ColorTranslator]::FromHtml('#F0F2B3')),
        39 * $scale,
        9 * $scale,
        16 * $scale,
        16 * $scale
    )

    $rearMountain = [System.Drawing.PointF[]]@(
        [System.Drawing.PointF]::new(5 * $scale, 45 * $scale),
        [System.Drawing.PointF]::new(21 * $scale, 22 * $scale),
        [System.Drawing.PointF]::new(31 * $scale, 34 * $scale),
        [System.Drawing.PointF]::new(41 * $scale, 17 * $scale),
        [System.Drawing.PointF]::new(59 * $scale, 45 * $scale)
    )
    $graphics.FillPolygon([System.Drawing.SolidBrush]::new([System.Drawing.ColorTranslator]::FromHtml('#4F9477')), $rearMountain)

    $frontMountain = [System.Drawing.PointF[]]@(
        [System.Drawing.PointF]::new(16 * $scale, 45 * $scale),
        [System.Drawing.PointF]::new(32 * $scale, 28 * $scale),
        [System.Drawing.PointF]::new(40 * $scale, 38 * $scale),
        [System.Drawing.PointF]::new(48 * $scale, 26 * $scale),
        [System.Drawing.PointF]::new(59 * $scale, 45 * $scale)
    )
    $graphics.FillPolygon([System.Drawing.SolidBrush]::new([System.Drawing.ColorTranslator]::FromHtml('#27624D')), $frontMountain)

    $river = [System.Drawing.Drawing2D.GraphicsPath]::new()
    $river.StartFigure()
    $river.AddBezier(4 * $scale, 45 * $scale, 16 * $scale, 41 * $scale, 19 * $scale, 53 * $scale, 33 * $scale, 47 * $scale)
    $river.AddBezier(33 * $scale, 47 * $scale, 43 * $scale, 42 * $scale, 50 * $scale, 45 * $scale, 60 * $scale, 49 * $scale)
    $river.AddLine(
        [System.Drawing.PointF]::new(60 * $scale, 49 * $scale),
        [System.Drawing.PointF]::new(60 * $scale, 64 * $scale)
    )
    $river.AddLine(
        [System.Drawing.PointF]::new(60 * $scale, 64 * $scale),
        [System.Drawing.PointF]::new(4 * $scale, 64 * $scale)
    )
    $river.CloseFigure()
    $graphics.FillPath([System.Drawing.SolidBrush]::new([System.Drawing.ColorTranslator]::FromHtml('#77CDE0')), $river)

    $highlight = [System.Drawing.Drawing2D.GraphicsPath]::new()
    $highlight.StartFigure()
    $highlight.AddBezier(4 * $scale, 52 * $scale, 17 * $scale, 48 * $scale, 21 * $scale, 59 * $scale, 34 * $scale, 53 * $scale)
    $highlight.AddBezier(34 * $scale, 53 * $scale, 44 * $scale, 48 * $scale, 51 * $scale, 52 * $scale, 60 * $scale, 55 * $scale)
    $highlight.AddLine(
        [System.Drawing.PointF]::new(60 * $scale, 55 * $scale),
        [System.Drawing.PointF]::new(60 * $scale, 64 * $scale)
    )
    $highlight.AddLine(
        [System.Drawing.PointF]::new(60 * $scale, 64 * $scale),
        [System.Drawing.PointF]::new(4 * $scale, 64 * $scale)
    )
    $highlight.CloseFigure()
    $highlightColor = [System.Drawing.Color]::FromArgb(184, 239, 252, 248)
    $graphics.FillPath([System.Drawing.SolidBrush]::new($highlightColor), $highlight)

    $graphics.Dispose()
    $background.Dispose()
    $river.Dispose()
    $highlight.Dispose()
    return $bitmap
}

$pngTargets = @{
    'favicon-16x16.png' = 16
    'favicon-32x32.png' = 32
    'apple-touch-icon.png' = 180
    'android-chrome-192x192.png' = 192
    'android-chrome-512x512.png' = 512
}

foreach ($target in $pngTargets.GetEnumerator()) {
    $bitmap = New-BrandIcon -Size $target.Value
    $path = Join-Path $resolvedOutput $target.Key
    $bitmap.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
    $bitmap.Dispose()
}

$icoSizes = @(16, 32, 48)
$pngPayloads = @()
foreach ($size in $icoSizes) {
    $bitmap = New-BrandIcon -Size $size
    $stream = [System.IO.MemoryStream]::new()
    $bitmap.Save($stream, [System.Drawing.Imaging.ImageFormat]::Png)
    $pngPayloads += ,@($size, $stream.ToArray())
    $stream.Dispose()
    $bitmap.Dispose()
}

$iconPath = Join-Path $resolvedOutput 'favicon.ico'
$writer = [System.IO.BinaryWriter]::new([System.IO.File]::Create($iconPath))
$writer.Write([uint16]0)
$writer.Write([uint16]1)
$writer.Write([uint16]$pngPayloads.Count)

$offset = 6 + (16 * $pngPayloads.Count)
foreach ($payload in $pngPayloads) {
    $size = [int]$payload[0]
    $bytes = [byte[]]$payload[1]
    $directorySize = if ($size -ge 256) { 0 } else { $size }
    $writer.Write([byte]$directorySize)
    $writer.Write([byte]$directorySize)
    $writer.Write([byte]0)
    $writer.Write([byte]0)
    $writer.Write([uint16]1)
    $writer.Write([uint16]32)
    $writer.Write([uint32]$bytes.Length)
    $writer.Write([uint32]$offset)
    $offset += $bytes.Length
}

foreach ($payload in $pngPayloads) {
    $writer.Write([byte[]]$payload[1])
}

$writer.Dispose()
