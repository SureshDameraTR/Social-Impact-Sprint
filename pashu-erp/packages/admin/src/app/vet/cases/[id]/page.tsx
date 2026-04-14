"use client";

import { useState, useEffect, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  Button,
  TextField,
  Chip,
  CircularProgress,
  Alert,
  Dialog,
  DialogContent,
  IconButton,
  Divider,
  Stack,
} from "@mui/material";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import CloseIcon from "@mui/icons-material/Close";
import PhotoCameraIcon from "@mui/icons-material/PhotoCamera";
import VideocamIcon from "@mui/icons-material/Videocam";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import AssignmentTurnedInIcon from "@mui/icons-material/AssignmentTurnedIn";
import SpeciesChip from "@/components/SpeciesChip";
import RiskBadge from "@/components/RiskBadge";
import { colors, sxCodeCell } from "@/theme/theme";
import { fmtDate } from "@/utils/format";
import { getCsrfToken } from "@/providers/auth-provider";

const API_URL = process.env.NEXT_PUBLIC_API_URL;

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface Owner {
  id: string;
  name: string;
  phone: string;
  village_code: string;
  location_district: string;
}

interface HealthEvent {
  id: string;
  event_date: string;
  event_type: string;
  symptoms: string[] | Record<string, unknown>;
  ai_risk_score: number;
  recommended_action: string;
  probable_diseases: unknown[];
}

interface Vaccination {
  id: string;
  vaccine_name: string;
  vaccination_date: string;
  next_due_date: string | null;
  administered_by: string | null;
}

interface AnimalDetail {
  id: string;
  species: string;
  name: string | null;
  breed: string;
  breed_type: string;
  sex: string;
  date_of_birth: string | null;
  pashu_aadhaar_id: string;
  tag_id: string | null;
  owner?: Owner;
  health_events?: HealthEvent[];
  vaccinations?: Vaccination[];
}

interface VetCaseDetail {
  id: string;
  animal_id: string;
  farmer_id: string;
  vet_id: string | null;
  status: string;
  priority: string;
  channel: string;
  farmer_notes: string | null;
  photo_urls: string[] | null;
  diagnosis: string | null;
  prescription: string | null;
  follow_up_date: string | null;
  video_call_url: string | null;
  district: string;
  created_at: string;
  updated_at: string;
  animal?: AnimalDetail;
  farmer?: { id: string; name: string; phone: string };
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function riskLabel(score: number): string {
  if (score >= 0.8) return "critical";
  if (score >= 0.6) return "high";
  if (score >= 0.3) return "medium";
  return "low";
}

function calcAge(dob: string | null): string {
  if (!dob) return "\u2014";
  const born = new Date(dob);
  if (isNaN(born.getTime())) return dob;
  const now = new Date();
  const months = (now.getFullYear() - born.getFullYear()) * 12 + (now.getMonth() - born.getMonth());
  if (months >= 12) {
    const years = Math.floor(months / 12);
    const rem = months % 12;
    return rem > 0 ? `${years}y ${rem}m` : `${years}y`;
  }
  return `${months}m`;
}

const priorityConfig: Record<string, { bg: string; color: string }> = {
  emergency: { bg: colors.errorLight, color: colors.accentRed },
  urgent: { bg: colors.warningLight, color: colors.accentAmber },
  routine: { bg: "#f0f0f0", color: "#666" },
};

const statusConfig: Record<string, { bg: string; color: string }> = {
  pending: { bg: colors.warningLight, color: colors.accentAmber },
  in_review: { bg: colors.infoLight, color: colors.accentBlue },
  diagnosed: { bg: colors.successLight, color: colors.accentGreen },
  closed: { bg: "#f0f0f0", color: "#666" },
};

const channelConfig: Record<string, { bg: string; color: string }> = {
  photo: { bg: colors.infoLight, color: colors.accentBlue },
  walk_in: { bg: colors.successLight, color: colors.accentGreen },
  referral: { bg: colors.warningLight, color: colors.accentAmber },
};

const eventTypeConfig: Record<string, { bg: string; color: string }> = {
  symptom: { bg: colors.warningLight, color: colors.accentAmber },
  treatment: { bg: colors.infoLight, color: colors.accentBlue },
  diagnosis: { bg: colors.successLight, color: colors.accentGreen },
  vaccination: { bg: colors.primaryLight, color: colors.primary },
  checkup: { bg: "#f0f0f0", color: "#666" },
};

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function VetCaseDetailPage() {
  const params = useParams();
  const router = useRouter();
  const caseId = params?.id as string;

  useEffect(() => {
    document.title = "Case Detail \u2014 PashuRaksha ERP";
  }, []);

  // State
  const [vetCase, setVetCase] = useState<VetCaseDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);

  // Form state
  const [diagnosis, setDiagnosis] = useState("");
  const [prescription, setPrescription] = useState("");
  const [followUpDate, setFollowUpDate] = useState("");
  const [videoCallUrl, setVideoCallUrl] = useState("");

  // Photo dialog
  const [photoDialogOpen, setPhotoDialogOpen] = useState(false);
  const [selectedPhoto, setSelectedPhoto] = useState<string | null>(null);

  // Fetch case detail
  const fetchCase = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_URL}/vet/cases/${caseId}`, {
        credentials: "include",
      });
      if (!res.ok) throw new Error(`API error ${res.status}`);
      const data: VetCaseDetail = await res.json();
      setVetCase(data);
      setDiagnosis(data.diagnosis ?? "");
      setPrescription(data.prescription ?? "");
      setFollowUpDate(data.follow_up_date ?? "");
      setVideoCallUrl(data.video_call_url ?? "");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load case");
    } finally {
      setIsLoading(false);
    }
  }, [caseId]);

  useEffect(() => {
    if (caseId) fetchCase();
  }, [caseId, fetchCase]);

  // PATCH helper
  const patchCase = useCallback(
    async (endpoint: string, body?: Record<string, unknown>) => {
      setActionLoading(endpoint);
      setActionError(null);
      setActionSuccess(null);
      try {
        const res = await fetch(`${API_URL}/vet/cases/${caseId}/${endpoint}`, {
          method: "PATCH",
          credentials: "include",
          headers: {
            "Content-Type": "application/json",
            "X-CSRF-Token": getCsrfToken(),
          },
          body: body ? JSON.stringify(body) : undefined,
        });
        if (!res.ok) {
          const errBody = await res.json().catch(() => ({}));
          throw new Error(
            (errBody as Record<string, string>).detail ?? `API error ${res.status}`
          );
        }
        const updated: VetCaseDetail = await res.json();
        setVetCase(updated);
        setActionSuccess(
          endpoint === "claim"
            ? "Case claimed successfully"
            : endpoint === "diagnose"
              ? "Diagnosis saved"
              : endpoint === "video-link"
                ? "Video link sent"
                : "Case closed"
        );
      } catch (err) {
        setActionError(err instanceof Error ? err.message : "Action failed");
      } finally {
        setActionLoading(null);
      }
    },
    [caseId]
  );

  // Action handlers
  const handleClaim = useCallback(() => patchCase("claim"), [patchCase]);

  const handleDiagnose = useCallback(() => {
    if (!diagnosis.trim()) return;
    patchCase("diagnose", {
      diagnosis: diagnosis.trim(),
      prescription: prescription.trim() || null,
      follow_up_date: followUpDate || null,
    });
  }, [patchCase, diagnosis, prescription, followUpDate]);

  const handleVideoLink = useCallback(() => {
    if (!videoCallUrl.trim()) return;
    patchCase("video-link", { video_call_url: videoCallUrl.trim() });
  }, [patchCase, videoCallUrl]);

  const handleClose = useCallback(() => patchCase("close"), [patchCase]);

  // Loading / error states
  if (isLoading) {
    return (
      <Box sx={{ display: "flex", justifyContent: "center", p: 8 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error || !vetCase) {
    return (
      <Box sx={{ p: 4 }}>
        <Alert severity="error">{error ?? "Case not found"}</Alert>
      </Box>
    );
  }

  const animal = vetCase.animal;
  const owner = animal?.owner ?? vetCase.farmer;
  const healthEvents = animal?.health_events ?? [];
  const vaccinations = animal?.vaccinations ?? [];
  const photos: string[] = Array.isArray(vetCase.photo_urls)
    ? vetCase.photo_urls
    : [];
  const isClaimed = vetCase.vet_id != null;
  const isClosed = vetCase.status === "closed";

  return (
    <Box p={3}>
      {/* Header */}
      <Stack direction="row" alignItems="center" spacing={1.5} mb={1}>
        <IconButton onClick={() => router.push("/vet/cases")} size="small">
          <ArrowBackIcon />
        </IconButton>
        <Typography variant="h4" sx={{ color: colors.text }}>
          Case Detail
        </Typography>
        <Chip
          label={vetCase.status.replace(/_/g, " ")}
          size="small"
          sx={{
            bgcolor: statusConfig[vetCase.status]?.bg ?? "#f0f0f0",
            color: statusConfig[vetCase.status]?.color ?? "#666",
            fontWeight: 600,
            fontSize: "11px",
            textTransform: "capitalize",
            border: "none",
          }}
        />
        <Chip
          label={vetCase.priority}
          size="small"
          sx={{
            bgcolor: priorityConfig[vetCase.priority]?.bg ?? "#f0f0f0",
            color: priorityConfig[vetCase.priority]?.color ?? "#666",
            fontWeight: 600,
            fontSize: "11px",
            textTransform: "capitalize",
            border: "none",
          }}
        />
        <Chip
          label={vetCase.channel.replace(/_/g, " ")}
          size="small"
          sx={{
            bgcolor: channelConfig[vetCase.channel]?.bg ?? colors.infoLight,
            color: channelConfig[vetCase.channel]?.color ?? colors.accentBlue,
            fontWeight: 600,
            fontSize: "11px",
            textTransform: "capitalize",
            border: "none",
          }}
        />
      </Stack>
      <Typography variant="body2" color="text.secondary" mb={3} ml={5.5}>
        Created {fmtDate(vetCase.created_at)} &middot; District: {vetCase.district}
      </Typography>

      {/* Action feedback */}
      {actionError && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setActionError(null)}>
          {actionError}
        </Alert>
      )}
      {actionSuccess && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setActionSuccess(null)}>
          {actionSuccess}
        </Alert>
      )}

      {/* Two-column layout */}
      <Grid container spacing={2.5}>
        {/* Left Column */}
        <Grid item xs={12} md={7}>
          {/* Farmer Info */}
          <Card sx={{ mb: 2.5 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Farmer Information
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="caption" color="text.secondary">
                    Name
                  </Typography>
                  <Typography variant="body1" sx={{ fontWeight: 500, color: colors.text }}>
                    {(owner as Owner)?.name ?? "\u2014"}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="caption" color="text.secondary">
                    Phone
                  </Typography>
                  <Typography variant="body1" sx={{ fontFamily: sxCodeCell.fontFamily, color: colors.textDim }}>
                    {(owner as Owner)?.phone ?? "\u2014"}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="caption" color="text.secondary">
                    Village
                  </Typography>
                  <Typography variant="body1" sx={{ color: colors.textDim }}>
                    {(owner as Owner)?.village_code ?? "\u2014"}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="caption" color="text.secondary">
                    District
                  </Typography>
                  <Typography variant="body1" sx={{ color: colors.textDim }}>
                    {(owner as Owner)?.location_district ?? vetCase.district}
                  </Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>

          {/* Animal Info */}
          <Card sx={{ mb: 2.5 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Animal Details
              </Typography>
              {animal ? (
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="text.secondary">
                      Species
                    </Typography>
                    <Box mt={0.5}>
                      <SpeciesChip species={animal.species} />
                    </Box>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="text.secondary">
                      Name
                    </Typography>
                    <Typography variant="body1" sx={{ fontWeight: 500, color: colors.text }}>
                      {animal.name ?? "\u2014"}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="text.secondary">
                      Breed
                    </Typography>
                    <Typography variant="body1" sx={{ color: colors.textDim }}>
                      {animal.breed} ({animal.breed_type})
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="text.secondary">
                      Age
                    </Typography>
                    <Typography variant="body1" sx={{ color: colors.textDim }}>
                      {calcAge(animal.date_of_birth)}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="text.secondary">
                      Pashu Aadhaar
                    </Typography>
                    <Typography
                      variant="body1"
                      sx={{ fontFamily: sxCodeCell.fontFamily, color: colors.textDim }}
                    >
                      {animal.pashu_aadhaar_id}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="text.secondary">
                      Sex
                    </Typography>
                    <Typography
                      variant="body1"
                      sx={{ textTransform: "capitalize", color: colors.textDim }}
                    >
                      {animal.sex}
                    </Typography>
                  </Grid>
                </Grid>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  Animal details not available.
                </Typography>
              )}
            </CardContent>
          </Card>

          {/* Photo Gallery */}
          <Card sx={{ mb: 2.5 }}>
            <CardContent>
              <Stack direction="row" alignItems="center" spacing={1} mb={1.5}>
                <PhotoCameraIcon sx={{ fontSize: 20, color: colors.textDim }} />
                <Typography variant="h6">Photos</Typography>
              </Stack>
              {photos.length === 0 ? (
                <Typography variant="body2" color="text.secondary" sx={{ py: 2, textAlign: "center" }}>
                  No photos submitted
                </Typography>
              ) : (
                <Box
                  sx={{
                    display: "grid",
                    gridTemplateColumns: "repeat(auto-fill, minmax(120px, 1fr))",
                    gap: 1.5,
                  }}
                >
                  {photos.map((url, i) => (
                    <Box
                      key={i}
                      onClick={() => {
                        setSelectedPhoto(url);
                        setPhotoDialogOpen(true);
                      }}
                      sx={{
                        width: "100%",
                        paddingTop: "100%",
                        position: "relative",
                        borderRadius: 2,
                        overflow: "hidden",
                        cursor: "pointer",
                        border: `1px solid ${colors.border}`,
                        "&:hover": { opacity: 0.85 },
                      }}
                    >
                      <Box
                        component="img"
                        src={url}
                        alt={`Case photo ${i + 1}`}
                        sx={{
                          position: "absolute",
                          top: 0,
                          left: 0,
                          width: "100%",
                          height: "100%",
                          objectFit: "cover",
                        }}
                      />
                    </Box>
                  ))}
                </Box>
              )}
            </CardContent>
          </Card>

          {/* Farmer Notes */}
          <Card sx={{ mb: 2.5 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Farmer&apos;s Notes
              </Typography>
              <Typography
                variant="body1"
                sx={{
                  color: vetCase.farmer_notes ? colors.text : colors.textLight,
                  whiteSpace: "pre-wrap",
                }}
              >
                {vetCase.farmer_notes || "No notes submitted by the farmer."}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Right Column */}
        <Grid item xs={12} md={5}>
          {/* Health History */}
          <Card sx={{ mb: 2.5 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Health History
              </Typography>
              {healthEvents.length === 0 ? (
                <Typography variant="body2" color="text.secondary" sx={{ py: 2, textAlign: "center" }}>
                  No health history recorded.
                </Typography>
              ) : (
                <Stack spacing={1.5}>
                  {[...healthEvents]
                    .sort((a, b) => new Date(b.event_date).getTime() - new Date(a.event_date).getTime())
                    .map((event) => (
                      <Box
                        key={event.id}
                        sx={{
                          p: 1.5,
                          borderRadius: 2,
                          bgcolor: colors.surfaceAlt,
                          border: `1px solid ${colors.border}`,
                        }}
                      >
                        <Stack direction="row" justifyContent="space-between" alignItems="center" mb={0.5}>
                          <Typography
                            variant="body2"
                            sx={{ fontFamily: sxCodeCell.fontFamily, color: colors.textDim }}
                          >
                            {fmtDate(event.event_date)}
                          </Typography>
                          <Stack direction="row" spacing={0.5}>
                            <Chip
                              label={event.event_type}
                              size="small"
                              sx={{
                                bgcolor: eventTypeConfig[event.event_type]?.bg ?? "#f0f0f0",
                                color: eventTypeConfig[event.event_type]?.color ?? "#666",
                                fontWeight: 600,
                                fontSize: "10px",
                                textTransform: "capitalize",
                                border: "none",
                              }}
                            />
                            <RiskBadge level={riskLabel(event.ai_risk_score)} />
                          </Stack>
                        </Stack>
                        <Typography variant="body2" sx={{ color: colors.text, mb: 0.5 }}>
                          {Array.isArray(event.symptoms)
                            ? event.symptoms.join(", ")
                            : typeof event.symptoms === "object" && event.symptoms
                              ? Object.keys(event.symptoms).join(", ")
                              : "\u2014"}
                        </Typography>
                        {event.recommended_action && (
                          <Typography variant="body2" sx={{ color: colors.textDim, fontSize: "12px" }}>
                            Action: {event.recommended_action}
                          </Typography>
                        )}
                      </Box>
                    ))}
                </Stack>
              )}
            </CardContent>
          </Card>

          {/* Vaccination History */}
          <Card sx={{ mb: 2.5 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Vaccination History
              </Typography>
              {vaccinations.length === 0 ? (
                <Typography variant="body2" color="text.secondary" sx={{ py: 2, textAlign: "center" }}>
                  No vaccination records.
                </Typography>
              ) : (
                <Stack spacing={1}>
                  {[...vaccinations]
                    .sort(
                      (a, b) =>
                        new Date(b.vaccination_date).getTime() -
                        new Date(a.vaccination_date).getTime()
                    )
                    .map((vax) => (
                      <Box
                        key={vax.id}
                        sx={{
                          p: 1.5,
                          borderRadius: 2,
                          bgcolor: colors.surfaceAlt,
                          border: `1px solid ${colors.border}`,
                        }}
                      >
                        <Stack direction="row" justifyContent="space-between" alignItems="center">
                          <Typography variant="body1" sx={{ fontWeight: 500, color: colors.text }}>
                            {vax.vaccine_name}
                          </Typography>
                          <Typography
                            variant="body2"
                            sx={{ fontFamily: sxCodeCell.fontFamily, color: colors.textDim }}
                          >
                            {fmtDate(vax.vaccination_date)}
                          </Typography>
                        </Stack>
                        {vax.next_due_date && (
                          <Typography variant="body2" sx={{ color: colors.textDim, fontSize: "12px", mt: 0.25 }}>
                            Next due: {fmtDate(vax.next_due_date)}
                          </Typography>
                        )}
                        {vax.administered_by && (
                          <Typography variant="body2" sx={{ color: colors.textLight, fontSize: "11px", mt: 0.25 }}>
                            By: {vax.administered_by}
                          </Typography>
                        )}
                      </Box>
                    ))}
                </Stack>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Action Section */}
      <Divider sx={{ my: 3 }} />

      {!isClaimed && !isClosed && (
        <Box sx={{ textAlign: "center", py: 2 }}>
          <Button
            variant="contained"
            size="large"
            startIcon={<AssignmentTurnedInIcon />}
            onClick={handleClaim}
            disabled={actionLoading === "claim"}
            sx={{
              bgcolor: colors.primary,
              "&:hover": { bgcolor: "#094d3f" },
              px: 5,
              py: 1.5,
            }}
          >
            {actionLoading === "claim" ? (
              <CircularProgress size={20} color="inherit" />
            ) : (
              "Claim Case"
            )}
          </Button>
        </Box>
      )}

      {isClaimed && !isClosed && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Vet Actions
          </Typography>
          <Grid container spacing={2.5}>
            {/* Diagnosis */}
            <Grid item xs={12} md={6}>
              <TextField
                label="Diagnosis"
                multiline
                rows={4}
                fullWidth
                value={diagnosis}
                onChange={(e) => setDiagnosis(e.target.value)}
                placeholder="Enter your diagnosis..."
              />
            </Grid>

            {/* Prescription */}
            <Grid item xs={12} md={6}>
              <TextField
                label="Prescription"
                multiline
                rows={4}
                fullWidth
                value={prescription}
                onChange={(e) => setPrescription(e.target.value)}
                placeholder="Enter prescription details..."
              />
            </Grid>

            {/* Follow-up date */}
            <Grid item xs={12} sm={6} md={4}>
              <TextField
                label="Follow-up Date"
                type="date"
                fullWidth
                value={followUpDate}
                onChange={(e) => setFollowUpDate(e.target.value)}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>

            {/* Save Diagnosis button */}
            <Grid item xs={12} sm={6} md={4} sx={{ display: "flex", alignItems: "flex-end" }}>
              <Button
                variant="contained"
                fullWidth
                startIcon={
                  actionLoading === "diagnose" ? (
                    <CircularProgress size={18} color="inherit" />
                  ) : (
                    <CheckCircleIcon />
                  )
                }
                onClick={handleDiagnose}
                disabled={!diagnosis.trim() || actionLoading === "diagnose"}
                sx={{
                  bgcolor: colors.primary,
                  "&:hover": { bgcolor: "#094d3f" },
                  py: 1.25,
                }}
              >
                Save Diagnosis
              </Button>
            </Grid>

            <Grid item xs={12}>
              <Divider />
            </Grid>

            {/* Video call URL */}
            <Grid item xs={12} sm={8}>
              <TextField
                label="Video Call URL"
                fullWidth
                value={videoCallUrl}
                onChange={(e) => setVideoCallUrl(e.target.value)}
                placeholder="Paste WhatsApp or JioMeet link"
              />
            </Grid>
            <Grid item xs={12} sm={4} sx={{ display: "flex", alignItems: "flex-end" }}>
              <Button
                variant="contained"
                fullWidth
                startIcon={
                  actionLoading === "video-link" ? (
                    <CircularProgress size={18} color="inherit" />
                  ) : (
                    <VideocamIcon />
                  )
                }
                onClick={handleVideoLink}
                disabled={!videoCallUrl.trim() || actionLoading === "video-link"}
                sx={{
                  bgcolor: colors.accentBlue,
                  "&:hover": { bgcolor: "#025e8c" },
                  py: 1.25,
                }}
              >
                Send Video Link
              </Button>
            </Grid>

            <Grid item xs={12}>
              <Divider />
            </Grid>

            {/* Close Case */}
            <Grid item xs={12} sx={{ display: "flex", justifyContent: "flex-end" }}>
              <Button
                variant="outlined"
                color="secondary"
                onClick={handleClose}
                disabled={actionLoading === "close"}
                sx={{
                  borderColor: colors.textDim,
                  color: colors.textDim,
                  "&:hover": { bgcolor: "#f5f5f5", borderColor: colors.text },
                }}
              >
                {actionLoading === "close" ? (
                  <CircularProgress size={18} sx={{ mr: 1 }} />
                ) : null}
                Close Case
              </Button>
            </Grid>
          </Grid>
        </Paper>
      )}

      {isClosed && (
        <Paper sx={{ p: 3, bgcolor: colors.surfaceAlt }}>
          <Typography variant="h6" gutterBottom>
            Case Closed
          </Typography>
          {vetCase.diagnosis && (
            <Box mb={2}>
              <Typography variant="caption" color="text.secondary">
                Diagnosis
              </Typography>
              <Typography variant="body1" sx={{ color: colors.text, whiteSpace: "pre-wrap" }}>
                {vetCase.diagnosis}
              </Typography>
            </Box>
          )}
          {vetCase.prescription && (
            <Box mb={2}>
              <Typography variant="caption" color="text.secondary">
                Prescription
              </Typography>
              <Typography variant="body1" sx={{ color: colors.text, whiteSpace: "pre-wrap" }}>
                {vetCase.prescription}
              </Typography>
            </Box>
          )}
          {vetCase.follow_up_date && (
            <Box mb={2}>
              <Typography variant="caption" color="text.secondary">
                Follow-up Date
              </Typography>
              <Typography variant="body1" sx={{ color: colors.textDim }}>
                {fmtDate(vetCase.follow_up_date)}
              </Typography>
            </Box>
          )}
          {vetCase.video_call_url && (
            <Box>
              <Typography variant="caption" color="text.secondary">
                Video Call URL
              </Typography>
              <Typography variant="body1" sx={{ color: colors.accentBlue }}>
                {vetCase.video_call_url}
              </Typography>
            </Box>
          )}
        </Paper>
      )}

      {/* Photo Dialog */}
      <Dialog
        open={photoDialogOpen}
        onClose={() => setPhotoDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogContent sx={{ p: 0, position: "relative" }}>
          <IconButton
            onClick={() => setPhotoDialogOpen(false)}
            sx={{
              position: "absolute",
              top: 8,
              right: 8,
              bgcolor: "rgba(0,0,0,0.5)",
              color: "#fff",
              "&:hover": { bgcolor: "rgba(0,0,0,0.7)" },
            }}
          >
            <CloseIcon />
          </IconButton>
          {selectedPhoto && (
            <Box
              component="img"
              src={selectedPhoto}
              alt="Case photo full size"
              sx={{
                width: "100%",
                maxHeight: "80vh",
                objectFit: "contain",
                display: "block",
              }}
            />
          )}
        </DialogContent>
      </Dialog>
    </Box>
  );
}
