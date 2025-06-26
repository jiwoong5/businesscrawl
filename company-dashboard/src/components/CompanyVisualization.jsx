import React, { useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";
import {
  Upload,
  FileText,
  Building2,
  MapPin,
  Factory,
  TrendingUp,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";

const CompanyVisualization = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [selectedView, setSelectedView] = useState("overview");
  const [selectedCompanyIndex, setSelectedCompanyIndex] = useState(0);

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setLoading(true);
    setError("");
    setSelectedCompanyIndex(0);

    try {
      const text = await file.text();
      const jsonData = JSON.parse(text);
      setData(jsonData);
    } catch (err) {
      setError("JSON 파일을 읽는 중 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  };

  // 지역별 업체 분포 데이터 처리
  const getRegionData = () => {
    if (!data) return [];

    const regionCount = {};
    data.forEach((company) => {
      const location = company["소재지"] || company["원본_소재지"] || "미상";
      const region = location.split(" ")[0] || "미상";
      regionCount[region] = (regionCount[region] || 0) + 1;
    });

    return Object.entries(regionCount)
      .map(([region, count]) => ({ region, count }))
      .sort((a, b) => b.count - a.count);
  };

  // 업종별 분포 데이터
  const getIndustryData = () => {
    if (!data) return [];

    const industryCount = {};
    data.forEach((company) => {
      const industry = company["대표업종"] || company["업종분류"] || "미상";
      const shortIndustry =
        industry.length > 15 ? industry.substring(0, 15) + "..." : industry;
      industryCount[shortIndustry] = (industryCount[shortIndustry] || 0) + 1;
    });

    return Object.entries(industryCount)
      .map(([industry, count]) => ({ industry, count }))
      .sort((a, b) => b.count - a.count);
  };

  // 종업원 수 분포 데이터
  const getEmployeeData = () => {
    if (!data) return [];

    const ranges = {
      "1-10명": 0,
      "11-50명": 0,
      "51-100명": 0,
      "101-500명": 0,
      "500명 이상": 0,
      미상: 0,
    };

    data.forEach((company) => {
      const employeeStr = company["종업원수"] || "";
      const employeeNum = parseInt(employeeStr.replace(/[^0-9]/g, ""));

      if (isNaN(employeeNum)) {
        ranges["미상"]++;
      } else if (employeeNum <= 10) {
        ranges["1-10명"]++;
      } else if (employeeNum <= 50) {
        ranges["11-50명"]++;
      } else if (employeeNum <= 100) {
        ranges["51-100명"]++;
      } else if (employeeNum <= 500) {
        ranges["101-500명"]++;
      } else {
        ranges["500명 이상"]++;
      }
    });

    return Object.entries(ranges)
      .map(([range, count]) => ({ range, count }))
      .filter((item) => item.count > 0);
  };

  // 화학물질 사용량 분석
  const getChemicalData = () => {
    if (!data) return [];

    const amountCodeMap = {
      "01": 1,
      "02": 10,
      "03": 100,
      "04": 1000,
      "05": 10000,
      "06": 100000,
    };

    const chemicalStats = [];
    data.forEach((company) => {
      const chemicals = company["화학물질정보"] || [];
      chemicals.forEach((chemical) => {
        const incomingCode = chemical["INCOMING_AMT_RANGE"];
        const incomingAmt = amountCodeMap[incomingCode] || 0;

        chemicalStats.push({
          company: company["업체명"] || "미상",
          chemical: chemical["MATTER_NM"] || chemical["CAS_NO"] || "미상",
          incomingAmountRange: incomingCode,
          deliveryAmountRange: chemical["DELIVERY_AMT_RANGE"] || "",
          casNo: chemical["CAS_NO"] || "",
          usage: incomingAmt, // 중요: 차트에서 사용됨
        });
      });
    });

    // usage 기준 내림차순 정렬
    return chemicalStats.sort((a, b) => b.usage - a.usage);
  };

  const COLORS = [
    "#0088FE",
    "#00C49F",
    "#FFBB28",
    "#FF8042",
    "#8884D8",
    "#82CA9D",
    "#FFC658",
    "#FF7C7C",
  ];

  // Overview 차트 렌더링
  const renderOverview = () => (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* 지역별 분포 */}
      <div className="bg-white p-6 rounded-lg shadow-lg">
        <h3 className="text-lg font-semibold mb-4 flex items-center">
          <MapPin className="mr-2" size={20} />
          지역별 업체 분포
        </h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={getRegionData()}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="region" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="count" fill="#0088FE" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* 업종별 분포 */}
      <div className="bg-white p-6 rounded-lg shadow-lg">
        <h3 className="text-lg font-semibold mb-4 flex items-center">
          <Factory className="mr-2" size={20} />
          업종별 분포
        </h3>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={getIndustryData()}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ industry, percent }) =>
                `${industry}: ${(percent * 100).toFixed(1)}%`
              }
              outerRadius={80}
              fill="#8884d8"
              dataKey="count"
            >
              {getIndustryData().map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={COLORS[index % COLORS.length]}
                />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* 종업원 수 분포 */}
      <div className="bg-white p-6 rounded-lg shadow-lg">
        <h3 className="text-lg font-semibold mb-4 flex items-center">
          <Building2 className="mr-2" size={20} />
          규모별 분포 (종업원 수)
        </h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={getEmployeeData()}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="range" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="count" fill="#00C49F" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* 화학물질 사용량 TOP 10 */}
      <div className="bg-white p-6 rounded-lg shadow-lg">
        <h3 className="text-lg font-semibold mb-4 flex items-center">
          <TrendingUp className="mr-2" size={20} />
          화학물질 사용량 TOP 10
        </h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={getChemicalData().slice(0, 10)} layout="horizontal">
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" />
            <YAxis dataKey="company" type="category" width={100} />
            <Tooltip
              formatter={(value) => [`${value.toLocaleString()}`, "사용량"]}
            />
            <Bar dataKey="usage" fill="#FF8042" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );

  // 한 업체씩 보여주고 좌우 버튼으로 넘기는 상세 정보 렌더링
  const renderDetailedCompany = () => {
    if (!data || data.length === 0) return <p>데이터가 없습니다.</p>;

    const company = data[selectedCompanyIndex];

    return (
      <div className="bg-white rounded-lg shadow-lg p-6 max-w-3xl mx-auto">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold flex items-center">
            <FileText className="mr-2" size={20} />
            업체 상세 정보
          </h3>

          <div className="flex space-x-2">
            <button
              onClick={() =>
                setSelectedCompanyIndex((idx) => Math.max(0, idx - 1))
              }
              disabled={selectedCompanyIndex === 0}
              className={`p-2 rounded ${
                selectedCompanyIndex === 0
                  ? "bg-gray-300 cursor-not-allowed"
                  : "bg-blue-500 text-white hover:bg-blue-600"
              }`}
              aria-label="이전 업체"
            >
              <ChevronLeft size={20} />
            </button>

            <button
              onClick={() =>
                setSelectedCompanyIndex((idx) =>
                  Math.min(data.length - 1, idx + 1)
                )
              }
              disabled={selectedCompanyIndex === data.length - 1}
              className={`p-2 rounded ${
                selectedCompanyIndex === data.length - 1
                  ? "bg-gray-300 cursor-not-allowed"
                  : "bg-blue-500 text-white hover:bg-blue-600"
              }`}
              aria-label="다음 업체"
            >
              <ChevronRight size={20} />
            </button>
          </div>
        </div>

        <p className="mb-2 text-gray-700 font-semibold text-xl">
          {company["업체명"] || company["원본_업체명"] || "업체명 미상"}
        </p>
        <p className="mb-4 text-gray-600">
          {company["소재지"] || company["원본_소재지"] || "주소 미상"}
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4 text-gray-800">
          <div>
            <p>
              <strong>대표자: </strong>
              {company["대표자"] || "미상"}
            </p>
            <p>
              <strong>업종: </strong>
              {company["대표업종"] || company["업종분류"] || "미상"}
            </p>
            <p>
              <strong>종업원 수: </strong>
              {company["종업원수"] || "미상"}
            </p>
          </div>
          <div>
            <p>
              <strong>설립년도: </strong>
              {company["설립년도"] || "미상"}
            </p>
            <p>
              <strong>자본금: </strong>
              {company["자본금"] || "미상"}
            </p>
            <p>
              <strong>매출액: </strong>
              {company["매출액"] || "미상"}
            </p>
          </div>
        </div>

        {company["화학물질정보"].map((chemical, idx) => (
          <div
            key={idx}
            className="bg-gray-50 border border-gray-200 rounded p-3"
          >
            <p>
              <strong>물질명: </strong>
              {chemical["MATTER_NM"] || "미상"}
            </p>
            <p>
              <strong>CAS No: </strong>
              {chemical["CAS_NO"] || "미상"}
            </p>
            <p>
              <strong>연간입고량: </strong>
              {chemical["INCOMING_AMT_RANGE"] || "미상"}
            </p>
            <p>
              <strong>연간사용판매량: </strong>
              {chemical["DELIVERY_AMT_RANGE"] || "미상"}
            </p>
          </div>
        ))}

        <p className="mt-4 text-gray-500 text-sm text-right">
          {selectedCompanyIndex + 1} / {data.length}
        </p>
      </div>
    );
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold mb-6 flex items-center text-gray-800">
        <Upload className="mr-3 text-blue-600" size={32} />
        업체 데이터 시각화
      </h1>
      {/* 파일 업로드 영역 */}
      {!data ? (
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-12 text-center bg-white shadow-md">
          <Upload className="mx-auto mb-4 text-gray-400" size={48} />
          <label
            htmlFor="file-upload"
            className="cursor-pointer inline-block text-lg font-medium text-gray-700 hover:text-blue-600"
          >
            크롤링 결과 JSON 파일을 업로드하세요
          </label>
          <input
            id="file-upload"
            type="file"
            accept=".json"
            onChange={handleFileUpload}
            className="hidden"
          />
          {loading && (
            <p className="mt-4 text-blue-600 font-semibold">
              파일을 읽는 중...
            </p>
          )}
          {error && <p className="mt-4 text-red-600 font-semibold">{error}</p>}
        </div>
      ) : (
        <>
          {/* 탭 영역 */}
          <div className="mb-6 flex space-x-4">
            <button
              className={`px-5 py-2 rounded-md font-semibold transition-colors duration-200 ${
                selectedView === "overview"
                  ? "bg-blue-600 text-white shadow-md"
                  : "bg-gray-200 text-gray-700 hover:bg-gray-300"
              }`}
              onClick={() => setSelectedView("overview")}
            >
              전체 개요
            </button>
            <button
              className={`px-5 py-2 rounded-md font-semibold transition-colors duration-200 ${
                selectedView === "detail"
                  ? "bg-blue-600 text-white shadow-md"
                  : "bg-gray-200 text-gray-700 hover:bg-gray-300"
              }`}
              onClick={() => setSelectedView("detail")}
            >
              업체 상세 정보
            </button>
          </div>
          {/* 뷰 */}
          {selectedView === "overview"
            ? renderOverview()
            : renderDetailedCompany()}
        </>
      )}
    </div>
  );
};

export default CompanyVisualization;
