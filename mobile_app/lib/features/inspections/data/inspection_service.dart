import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';
import '../../../core/network/api_client.dart';
import '../../../core/network/api_config.dart';
import '../../alerts/data/models/alert_model.dart';
import 'models/inspection_model.dart';

class InspectionService {
  const InspectionService({this.apiClient = const ApiClient()});

  final ApiClient apiClient;

  Future<List<AlertModel>> fetchInspections() async {
    final inspections = await fetchInspectionModels();
    return inspections.map((inspection) => inspection.toAlertModel()).toList();
  }

  Future<List<InspectionModel>> fetchInspectionModels() async {
    final json = await apiClient.get('/api/inspections/') as List<dynamic>;
    return json
        .whereType<Map<String, dynamic>>()
        .map(InspectionModel.fromJson)
        .toList();
  }

  Future<InspectionModel> fetchInspectionDetail(String id) async {
    final json = await apiClient.get('/api/inspections/$id/') as Map<String, dynamic>;
    return InspectionModel.fromJson(json);
  }

  Future<DashboardStats> fetchDashboardStats() async {
    final json = await apiClient.get('/stats/') as Map<String, dynamic>;
    return DashboardStats.fromJson(json);
  }

  Future<InspectionModel> uploadInspection({
    required List<int> bytes,
    required String filename,
    required String cameraId,
    bool isVideo = false,
  }) async {
    final uri = ApiConfig.uri('/api/upload/');
    final request = http.MultipartRequest('POST', uri);
    request.fields['camera_id'] = cameraId;

    final multipartFile = http.MultipartFile.fromBytes(
      isVideo ? 'video' : 'image',
      bytes,
      filename: filename,
      contentType: MediaType(
        isVideo ? 'video' : 'image',
        filename.split('.').last,
      ),
    );
    request.files.add(multipartFile);

    final streamedResponse = await request.send();
    final response = await http.Response.fromStream(streamedResponse);

    if (response.statusCode >= 200 && response.statusCode < 300) {
      final decodedBody = jsonDecode(response.body);
      if (decodedBody is Map<String, dynamic>) {
        return InspectionModel.fromJson(decodedBody);
      }
      throw Exception('Invalid server response format.');
    } else {
      final decodedBody = jsonDecode(response.body);
      final error = decodedBody is Map ? (decodedBody['detail'] ?? decodedBody['error'] ?? 'Upload failed.') : 'Upload failed.';
      throw Exception(error);
    }
  }
}
