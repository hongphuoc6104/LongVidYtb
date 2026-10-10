# Technical Issue & Lesson Learned Log Template

When discovering and resolving a new issue not yet indexed in the system, the Agent or engineer must create a log file at:
`sys/logs/issues/<timestamp_ns>-<job_id>-<module>.md`

Standard template structure:

```markdown
# Issue [Job ID] — [Affected Subsystem]

- **Date Recorded**: YYYY-MM-DD HH:MM:SS
- **Job ID**: [job_id]
- **Subsystem**: [content | audio | images | render | pipeline]
- **Status**: Resolved

---

## 1. Concrete Symptoms
- Triggering Command: `...`
- Error Message / Traceback:
  ```text
  [Paste log or error output here]
  ```
- Observed Behavior: [Detailed description of interface or output artifact defects]

---

## 2. Root Cause
- [Clear analysis of why the error occurred: headless environment, network timeout, missing Chrome flags, version discrepancy, etc.]

---

## 3. Proven Remedies
1. **Concrete Resolution Steps**:
   - Step 1: ...
   - Step 2: ...
2. **Diff or Code Modifications**:
   - [Modified file paths]
3. **Live Verification Evidence**:
   - Successfully generated artifact or video: `...`
   - Test results: `pytest ...` (6/6 passed)
   - Measurement results from `ffprobe`: [Actual measured parameters]
```

After creating the issue file, append a one-line summary entry into the index table at [`sys/logs/issues/INDEX.md`](file:///home/hongphuoc6104/Desktop/flowkit-video-pipeline/sys/logs/issues/INDEX.md).
