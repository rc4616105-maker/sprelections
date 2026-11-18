/**
 * Election Configuration & Candidate Data
 * Matching Main Web Theme with 6 Houses & 4 Leadership Posts
 */

const DEFAULT_HOUSES = [
  {
    id: "bheeshma",
    name: "Bheeshma",
    fullName: "Bheeshma House",
    color: "#EAB308",      // Warm Yellow / Amber
    accent: "#CA8A04",
    textColor: "#111827",
    motto: "Unwavering Resolve & Duty",
    candidates: {
      boys_captain: {
        postTitle: "Boys Captain",
        name: "Arjun Verma",
        grade: "Grade 12-A",
        photo: "",
        quote: "Leadership is action, not position."
      },
      girls_captain: {
        postTitle: "Girls Captain",
        name: "Ananya Iyer",
        grade: "Grade 12-B",
        photo: "",
        quote: "Together we strive, together we thrive."
      },
      boys_vc: {
        postTitle: "Boys Vice-Captain",
        name: "Rohan Nair",
        grade: "Grade 11-A",
        photo: "",
        quote: "Service with humility and courage."
      },
      girls_vc: {
        postTitle: "Girls Vice-Captain",
        name: "Sneha Reddy",
        grade: "Grade 11-C",
        photo: "",
        quote: "Empowering every student voice."
      }
    }
  },
  {
    id: "gurudrona",
    name: "Gurudrona",
    fullName: "Gurudrona House",
    color: "#2563EB",      // Vibrant Royal Blue
    accent: "#1D4ED8",
    textColor: "#FFFFFF",
    motto: "Discipline, Mastery & Focus",
    candidates: {
      boys_captain: {
        postTitle: "Boys Captain",
        name: "Devrath Singh",
        grade: "Grade 12-B",
        photo: "",
        quote: "Aim high, strike true."
      },
      girls_captain: {
        postTitle: "Girls Captain",
        name: "Kavya Menon",
        grade: "Grade 12-C",
        photo: "",
        quote: "Excellence through relentless practice."
      },
      boys_vc: {
        postTitle: "Boys Vice-Captain",
        name: "Kunal Joshi",
        grade: "Grade 11-B",
        photo: "",
        quote: "Steadfast guidance for every teammate."
      },
      girls_vc: {
        postTitle: "Girls Vice-Captain",
        name: "Meera Sen",
        grade: "Grade 11-A",
        photo: "",
        quote: "Inspiring strength through knowledge."
      }
    }
  },
  {
    id: "hanuman",
    name: "Hanuman",
    fullName: "Hanuman House",
    color: "#EA580C",      // Vibrant Orange
    accent: "#C2410C",
    textColor: "#FFFFFF",
    motto: "Courage, Loyalty & Unstoppable Might",
    candidates: {
      boys_captain: {
        postTitle: "Boys Captain",
        name: "Tejas Chawla",
        grade: "Grade 12-B",
        photo: "",
        quote: "No peak is too high to conquer."
      },
      girls_captain: {
        postTitle: "Girls Captain",
        name: "Ishita Pillai",
        grade: "Grade 12-C",
        photo: "",
        quote: "Boundless energy, limitless devotion."
      },
      boys_vc: {
        postTitle: "Boys Vice-Captain",
        name: "Dhruv Kapoor",
        grade: "Grade 11-B",
        photo: "",
        quote: "Courage is contagious."
      },
      girls_vc: {
        postTitle: "Girls Vice-Captain",
        name: "Avni Sharma",
        grade: "Grade 11-A",
        photo: "",
        quote: "Strength begins with unity."
      }
    }
  },
  {
    id: "karna",
    name: "Karna",
    fullName: "Karna House",
    color: "#DC2626",      // Crimson Red
    accent: "#B91C1C",
    textColor: "#FFFFFF",
    motto: "Selfless Honor & Supreme Bravery",
    candidates: {
      boys_captain: {
        postTitle: "Boys Captain",
        name: "Abhimanyu Das",
        grade: "Grade 12-A",
        photo: "",
        quote: "Standing firm when the storm rages."
      },
      girls_captain: {
        postTitle: "Girls Captain",
        name: "Tarini Mukherjee",
        grade: "Grade 12-C",
        photo: "",
        quote: "Honor over glory, duty over triumph."
      },
      boys_vc: {
        postTitle: "Boys Vice-Captain",
        name: "Siddharth Jain",
        grade: "Grade 11-A",
        photo: "",
        quote: "Loyal to the team, faithful to the cause."
      },
      girls_vc: {
        postTitle: "Girls Vice-Captain",
        name: "Roshni Paul",
        grade: "Grade 11-B",
        photo: "",
        quote: "Unyielding spirit, unwavering heart."
      }
    }
  },
  {
    id: "vasistha",
    name: "Vasistha",
    fullName: "Vasistha House",
    color: "#DB2777",      // Vibrant Rose Pink
    accent: "#BE185D",
    textColor: "#FFFFFF",
    motto: "Wisdom, Peace & Integrity",
    candidates: {
      boys_captain: {
        postTitle: "Boys Captain",
        name: "Aditya Hegde",
        grade: "Grade 12-A",
        photo: "",
        quote: "True power lies in quiet conviction."
      },
      girls_captain: {
        postTitle: "Girls Captain",
        name: "Pooja Kulkarni",
        grade: "Grade 12-A",
        photo: "",
        quote: "Compassion and character above all."
      },
      boys_vc: {
        postTitle: "Boys Vice-Captain",
        name: "Varun Bhat",
        grade: "Grade 11-C",
        photo: "",
        quote: "Leading by standing beside you."
      },
      girls_vc: {
        postTitle: "Girls Vice-Captain",
        name: "Tanvi Saxena",
        grade: "Grade 11-B",
        photo: "",
        quote: "Harmonious hearts build great houses."
      }
    }
  },
  {
    id: "vishwamithra",
    name: "Vishwamithra",
    fullName: "Vishwamithra House",
    color: "#7C3AED",      // Royal Purple
    accent: "#6D28D9",
    textColor: "#FFFFFF",
    motto: "Audacity, Innovation & Valor",
    candidates: {
      boys_captain: {
        postTitle: "Boys Captain",
        name: "Vikramaditya Roy",
        grade: "Grade 12-C",
        photo: "",
        quote: "Creating new horizons where none exist."
      },
      girls_captain: {
        postTitle: "Girls Captain",
        name: "Rhea Deshmukh",
        grade: "Grade 12-B",
        photo: "",
        quote: "Fearless pursuit of greatness."
      },
      boys_vc: {
        postTitle: "Boys Vice-Captain",
        name: "Samarth Rao",
        grade: "Grade 11-A",
        photo: "",
        quote: "Resilience in every challenge."
      },
      girls_vc: {
        postTitle: "Girls Vice-Captain",
        name: "Pari Chopra",
        grade: "Grade 11-C",
        photo: "",
        quote: "Breaking barriers with bold determination."
      }
    }
  }
];

const POST_KEYS = ["boys_captain", "girls_captain", "boys_vc", "girls_vc"];

const POST_METADATA = {
  boys_captain: { title: "Boys Captain", badge: "Boys Captain" },
  girls_captain: { title: "Girls Captain", badge: "Girls Captain" },
  boys_vc: { title: "Boys Vice-Captain", badge: "Vice Captain" },
  girls_vc: { title: "Girls Vice-Captain", badge: "Vice Captain" }
};

/**
 * 5 School Cabinet (Central Council) Apex Posts
 */
const DEFAULT_CABINET_POSTS = [
  {
    id: "PRESIDENT",
    code: "Vote_President",
    name: "President",
    fullName: "School President",
    color: "#059669",
    accent: "#047857",
    textColor: "#FFFFFF",
    grade: "Class 10",
    postTitle: "School President",
    candidate: {
      name: "Awaiting Result",
      grade: "Class 10 · Central Cabinet",
      photo: "",
      quote: "Apex Student Leadership"
    }
  },
  {
    id: "VICE_PRESIDENT",
    code: "Vote_Vice_President",
    name: "Vice Pres",
    fullName: "School Vice President",
    color: "#0D9488",
    accent: "#0F766E",
    textColor: "#FFFFFF",
    grade: "Class 9",
    postTitle: "School Vice President",
    candidate: {
      name: "Awaiting Result",
      grade: "Class 9 · Central Cabinet",
      photo: "",
      quote: "Supporting the Student Voice"
    }
  },
  {
    id: "LITERARY_SECRETARY",
    code: "Vote_Literary_Sec",
    name: "Literary Sec",
    fullName: "Literary Secretary",
    color: "#7C3AED",
    accent: "#6D28D9",
    textColor: "#FFFFFF",
    grade: "Class 9",
    postTitle: "Literary Secretary",
    candidate: {
      name: "Awaiting Result",
      grade: "Class 9 · Central Cabinet",
      photo: "",
      quote: "Expression, Oratory & Eloquence"
    }
  },
  {
    id: "SPORTS_SECRETARY",
    code: "Vote_Sports_Sec",
    name: "Sports Sec",
    fullName: "Sports Secretary",
    color: "#EA580C",
    accent: "#C2410C",
    textColor: "#FFFFFF",
    grade: "Class 9",
    postTitle: "Sports Secretary",
    candidate: {
      name: "Awaiting Result",
      grade: "Class 9 · Central Cabinet",
      photo: "",
      quote: "Excellence in Sportsmanship"
    }
  },
  {
    id: "SOCIAL_CULTURAL_SECRETARY",
    code: "Vote_Social_Cultural_Sec",
    name: "Cultural Sec",
    fullName: "Social & Cultural Secretary",
    color: "#D97706",
    accent: "#B45309",
    textColor: "#FFFFFF",
    grade: "Class 9",
    postTitle: "Social & Cultural Secretary",
    candidate: {
      name: "Awaiting Result",
      grade: "Class 9 · Central Cabinet",
      photo: "",
      quote: "Creativity, Unity & Culture"
    }
  }
];
