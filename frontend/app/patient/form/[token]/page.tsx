interface PatientFormPageProps {
  params: Promise<{
    token: string;
  }>;
}

export default async function PatientFormPage({ params }: PatientFormPageProps) {
  const { token } = await params;
  
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="max-w-md w-full space-y-8 p-8">
        <div className="text-center">
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
            Patient Form
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Token: {token}
          </p>
          <p className="mt-4 text-sm text-gray-500">
            This page is under development.
          </p>
        </div>
      </div>
    </div>
  );
}
