<?php

namespace App\Http\Controllers;

use App\Exceptions\AiServiceException;
use App\Http\Requests\ScanRequest;
use App\Services\CollectionService;
use App\Services\FactsheetService;
use App\Services\FastApiClient;
use Illuminate\Support\Facades\Log;

class ScanController extends Controller
{
    public function store(
        ScanRequest $request,
        FastApiClient $ai,
        FactsheetService $factsheets,
        CollectionService $collection
    ) {
        try {
            $aiResult = $ai->predict($request->file('image'));
        } catch (AiServiceException $e) {
            Log::error('AI service error: ' . $e->getMessage());

            return response()->json([
                'status' => 'error',
                'code' => 'ai_unavailable',
                'message' => 'Error 503: backend FastAPI sedang down.',
            ], 503);
        }

        $detections = [];

        foreach ($aiResult['detections'] as $detection) {
            $animal = $factsheets->findByClassId($detection['class_id']);

            if ($animal === null) {
                continue;
            }

            $outcome = $collection->record(
                $request->user(),
                $animal,
                $detection,
                $aiResult['image_width'],
                $aiResult['image_height']
            );

            $detections[] = [
                'class_id' => $detection['class_id'],
                'confidence' => $detection['confidence'],
                'bbox' => $detection['bbox'],
                'animal' => $factsheets->format($animal),
                'is_new_discovery' => $outcome['is_new_discovery'],
                'badge' => $outcome['badge'],
            ];
        }

        if ($detections === []) {
            return response()->json([
                'status' => 'error',
                'code' => 'no_animal_detected',
                'message' => 'Satwa tidak dikenali.',
            ], 422);
        }

        return response()->json([
            'status' => 'success',
            'image' => [
                'width' => $aiResult['image_width'],
                'height' => $aiResult['image_height'],
            ],
            'detections' => $detections,
            'progress' => $collection->progress($request->user()),
        ]);
    }
}