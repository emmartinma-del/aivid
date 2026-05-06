import { getServerSession } from "next-auth";
import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
  const session = await getServerSession();
  if (!session) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const body = await req.json();
  const { projectId, filename, mimeType, assetType } = body;

  const res = await fetch(
    `${process.env.NEXT_PUBLIC_API_URL}/api/v1/projects/${projectId}/assets/upload-url`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${(session as any).accessToken}`,
      },
      body: JSON.stringify({ filename, mime_type: mimeType, asset_type: assetType }),
    }
  );

  const data = await res.json();
  return NextResponse.json(data, { status: res.status });
}
