import { useState, useEffect, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Button,
  TextField,
  Chip,
  Divider,
  Skeleton,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from "@mui/material";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import VideocamIcon from "@mui/icons-material/Videocam";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import AssignmentIndIcon from "@mui/icons-material/AssignmentInd";
import SpeciesChip from "../components/SpeciesChip";
import { colors } from "../theme";
import { fmtDate, fmtDateTime } from "../utils/format";
import {
  getCaseDetail,
  claimCase,
  diagnoseCase,
  setVideoLink,
  closeCase,
  type VetCase,
} from "../api/vet";

export default function CaseDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [vetCase, setVetCase] = useState<VetCase | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [actionLoading, setActionLoading] = useState(false);

  // Diagnose dialog
  const [diagOpen, setDiagOpen] = useState(false);
  const [diagnosis, setDiagnosis] = useState("");
  const [prescription, setPrescription] = useState("");
  const [followUpDate, setFollowUpDate] = useState("");

  // Video link dialog
  const [videoOpen, setVideoOpen] = useState(false);
  const [videoUrl, setVideoUrl] = useState("");

  const load = useCallback(async () => {
    if (!id) return;
    setLoading(true);
    try {
      const res = await getCaseDetail(id);
      setVetCase(res.data);
    } catch {
      setError("Failed to load case details");
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => { load(); }, [load]);

  const handleClaim = async () => {
    if (!id) return;
    setActionLoading(true);
    try {
      await claimCase(id);
      await load();
    } catch {
      setError("Failed to claim case");
    } finally {
      setActionLoading(false);
    }
  };

  const handleDiagnose = async () => {
    if (!id || !diagnosis || !prescription) return;
    setActionLoading(true);
    try {
      await diagnoseCase(id, {
        diagnosis,
        prescription,
        follow_up_date: followUpDate || undefined,
      });
      setDiagOpen(false);
      await load();
    } catch {
      setError("Failed to submit diagnosis");
    } finally {
      setActionLoading(false);
    }
  };

  const handleVideoLink = async () => {
    if (!id || !videoUrl) return;
    setActionLoading(true);
    try {
      await setVideoLink(id, videoUrl);
      setVideoOpen(false);
      await load();
    } catch {
      setError("Failed to set video link");
    } finally {
      setActionLoading(false);
    }
  };

  const handleClose = async () => {
    if (!id) return;
    setActionLoading(true);
    try {
      await closeCase(id);
      await load();
    } catch {
      setError("Failed to close case");
    } finally {
      setActionLoading(false);
    }
  };

  const statusColor = (status: string) => {
    const key = status as keyof typeof colors;
    return colors[key] || colors.routine;
  };

  if (loading) {
    return (
      <Box sx={{ p: 3, maxWidth: 900, mx: "auto" }}>
        <Skeleton variant="rounded" height={60} sx={{ mb: 2 }} />
        <Skeleton variant="rounded" height={400} />
      </Box>
    );
  }

  if (!vetCase) {
    return (
      <Box sx={{ p: 3, maxWidth: 900, mx: "auto" }}>
        <Alert severity="error">Case not found</Alert>
      </Box>
    );
  }

  const c = vetCase;
  const sc = statusColor(c.status);

  return (
    <Box sx={{ p: 3, maxWidth: 900, mx: "auto" }}>
      <Button startIcon={<ArrowBackIcon />} onClick={() => navigate("/cases")} sx={{ mb: 2 }}>
        Back to Cases
      </Button>

      {error && <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError("")}>{error}</Alert>}

      {/* Header */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: 1 }}>
            <Box>
              <Typography variant="h5" fontWeight={700}>
                {c.animal?.name || c.animal?.species || "Animal"} — Case
              </Typography>
              <Typography variant="body2" color="text.secondary">
                ID: {c.id.slice(0, 8)} &middot; Created {fmtDateTime(c.created_at)}
              </Typography>
            </Box>
            <Box sx={{ display: "flex", gap: 1 }}>
              <Chip
                label={c.status.replace("_", " ")}
                sx={{ bgcolor: sc.bg, color: sc.text, fontWeight: 700, textTransform: "capitalize" }}
              />
              <Chip
                label={c.priority}
                sx={{
                  bgcolor: (colors[c.priority as keyof typeof colors] || colors.routine).bg,
                  color: (colors[c.priority as keyof typeof colors] || colors.routine).text,
                  fontWeight: 700,
                  textTransform: "capitalize",
                }}
              />
            </Box>
          </Box>
        </CardContent>
      </Card>

      <Grid container spacing={3}>
        {/* Animal & Farmer Info */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: "100%" }}>
            <CardContent>
              <Typography variant="subtitle1" fontWeight={700} sx={{ mb: 2 }}>
                Animal Details
              </Typography>
              {c.animal ? (
                <>
                  <InfoRow label="Species" value={<SpeciesChip species={c.animal.species} />} />
                  <InfoRow label="Name" value={c.animal.name || "—"} />
                  <InfoRow label="Breed" value={c.animal.breed} />
                  <InfoRow label="ID" value={c.animal.id.slice(0, 12)} />
                </>
              ) : (
                <Typography color="text.secondary">No animal data</Typography>
              )}

              <Divider sx={{ my: 2 }} />

              <Typography variant="subtitle1" fontWeight={700} sx={{ mb: 2 }}>
                Farmer Details
              </Typography>
              {c.animal?.owner ? (
                <>
                  <InfoRow label="Name" value={c.animal.owner.name} />
                  <InfoRow label="Phone" value={c.animal.owner.phone} />
                  <InfoRow label="Village" value={c.animal.owner.village_code} />
                  <InfoRow label="District" value={c.animal.owner.location_district} />
                </>
              ) : c.farmer ? (
                <InfoRow label="Name" value={c.farmer.name} />
              ) : (
                <Typography color="text.secondary">No farmer data</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Case Details */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: "100%" }}>
            <CardContent>
              <Typography variant="subtitle1" fontWeight={700} sx={{ mb: 2 }}>
                Case Information
              </Typography>
              <InfoRow label="Channel" value={c.channel.replace("_", " ")} />
              <InfoRow label="District" value={c.district} />
              <InfoRow label="Farmer Notes" value={c.farmer_notes || "—"} />
              <InfoRow label="Updated" value={fmtDateTime(c.updated_at)} />

              {c.photo_urls && c.photo_urls.length > 0 && (
                <>
                  <Divider sx={{ my: 2 }} />
                  <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 1 }}>
                    Photos ({c.photo_urls.length})
                  </Typography>
                  <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
                    {c.photo_urls
                      .filter((u) => u.startsWith("/") || u.startsWith("https://"))
                      .map((url, i) => (
                        <Box
                          key={i}
                          component="img"
                          src={url}
                          alt={`Photo ${i + 1}`}
                          sx={{ width: 80, height: 80, borderRadius: 1, objectFit: "cover" }}
                        />
                      ))}
                  </Box>
                </>
              )}

              {c.video_call_url && c.video_call_url.startsWith("https://") && (
                <>
                  <Divider sx={{ my: 2 }} />
                  <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 1 }}>
                    Video Consultation
                  </Typography>
                  <Button
                    variant="outlined"
                    startIcon={<VideocamIcon />}
                    href={c.video_call_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    size="small"
                  >
                    Join Video Call
                  </Button>
                </>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Diagnosis */}
        {(c.diagnosis || c.prescription || c.follow_up_date) && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="subtitle1" fontWeight={700} sx={{ mb: 2 }}>
                  Diagnosis & Treatment
                </Typography>
                <InfoRow label="Diagnosis" value={c.diagnosis || "—"} />
                <InfoRow label="Prescription" value={c.prescription || "—"} />
                <InfoRow label="Follow-up" value={fmtDate(c.follow_up_date)} />
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>

      {/* Actions */}
      <Box sx={{ display: "flex", gap: 2, mt: 3, flexWrap: "wrap" }}>
        {c.status === "pending" && (
          <Button
            variant="contained"
            startIcon={<AssignmentIndIcon />}
            onClick={handleClaim}
            disabled={actionLoading}
          >
            Claim Case
          </Button>
        )}
        {(c.status === "pending" || c.status === "in_review") && (
          <>
            <Button
              variant="contained"
              color="success"
              startIcon={<CheckCircleIcon />}
              onClick={() => setDiagOpen(true)}
              disabled={actionLoading}
            >
              Diagnose
            </Button>
            <Button
              variant="outlined"
              startIcon={<VideocamIcon />}
              onClick={() => setVideoOpen(true)}
              disabled={actionLoading}
            >
              Set Video Link
            </Button>
          </>
        )}
        {c.status === "diagnosed" && (
          <Button
            variant="contained"
            color="info"
            onClick={handleClose}
            disabled={actionLoading}
          >
            Close Case
          </Button>
        )}
      </Box>

      {/* Diagnose Dialog */}
      <Dialog open={diagOpen} onClose={() => setDiagOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Submit Diagnosis</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Diagnosis"
            multiline
            rows={3}
            value={diagnosis}
            onChange={(e) => setDiagnosis(e.target.value)}
            sx={{ mt: 1, mb: 2 }}
          />
          <TextField
            fullWidth
            label="Prescription"
            multiline
            rows={3}
            value={prescription}
            onChange={(e) => setPrescription(e.target.value)}
            sx={{ mb: 2 }}
          />
          <TextField
            fullWidth
            label="Follow-up Date"
            type="date"
            value={followUpDate}
            onChange={(e) => setFollowUpDate(e.target.value)}
            InputLabelProps={{ shrink: true }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDiagOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleDiagnose}
            disabled={!diagnosis || !prescription || actionLoading}
          >
            Submit
          </Button>
        </DialogActions>
      </Dialog>

      {/* Video Link Dialog */}
      <Dialog open={videoOpen} onClose={() => setVideoOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Set Video Call Link</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Video Call URL"
            placeholder="https://meet.google.com/..."
            value={videoUrl}
            onChange={(e) => setVideoUrl(e.target.value)}
            sx={{ mt: 1 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setVideoOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleVideoLink}
            disabled={!videoUrl || actionLoading}
          >
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

function InfoRow({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <Box sx={{ display: "flex", py: 0.75, gap: 1 }}>
      <Typography variant="body2" color="text.secondary" sx={{ minWidth: 100, flexShrink: 0 }}>
        {label}
      </Typography>
      <Typography variant="body2" fontWeight={500} sx={{ wordBreak: "break-word" }} component="div">
        {value}
      </Typography>
    </Box>
  );
}
