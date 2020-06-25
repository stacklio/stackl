{{/* vim: set filetype=mustache: */}}
{{/*
Expand the name of the chart.
*/}}
{{- define "stackl.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "stackl.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- $name := default .Chart.Name .Values.nameOverride -}}
{{- if contains $name .Release.Name -}}
{{- .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}
{{- end -}}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "stackl.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Common labels
*/}}
{{- define "stackl.labels" -}}
helm.sh/chart: {{ include "stackl.chart" . }}
{{ include "stackl.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}

{{/*
Selector labels
*/}}
{{- define "stackl.selectorLabels" -}}
app.kubernetes.io/name: {{ include "stackl.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{/*
Create the name of the service account to use
*/}}
{{- define "stackl.serviceAccountName" -}}
{{- if .Values.serviceAccount.create -}}
    {{ default (include "stackl.fullname" .) .Values.serviceAccount.name }}
{{- else -}}
    {{ default "default" .Values.serviceAccount.name }}
{{- end -}}
{{- end -}}

{{- define "stackl.redis" -}}
  {{- printf "%s-redis" (include "stackl.fullname" .) -}}
{{- end -}}

{{- define "stackl.rest" -}}
  {{- printf "%s-rest" (include "stackl.fullname" .) -}}
{{- end -}}

{{- define "stackl.worker" -}}
  {{- printf "%s-worker" (include "stackl.fullname" .) -}}
{{- end -}}

{{- define "stackl.opa" -}}
  {{- printf "%s-opa" (include "stackl.fullname" .) -}}
{{- end -}}

{{- define "stackl.job-broker" -}}
  {{- printf "%s-job-broker" (include "stackl.fullname" .) -}}
{{- end -}}