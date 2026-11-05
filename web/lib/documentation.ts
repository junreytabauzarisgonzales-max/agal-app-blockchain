export interface StoryPhoto {
  id: string;
  width: number;
  height: number;
  alt: string;
  caption: string;
}

export interface StoryChapter {
  id: string;
  number: string;
  label: string;
  title: string;
  summary: string;
  paragraphs: string[];
  status: "Completed" | "Ongoing";
  photos: StoryPhoto[];
}

export const storyHeroPhoto: StoryPhoto = {
  id: "farmer-team", width: 960, height: 720,
  alt: "Four people standing together beside a green boat during the Agal farmer field visits.",
  caption: "A shared moment during the farmer visits.",
};

// Chapter order, championship, and current destination were confirmed by the
// team. Keep dates and interview findings out of the story until supplied.
export const storyChapters: StoryChapter[] = [
  {
    id: "mentoring",
    number: "01",
    label: "Mentoring",
    title: "Preparing for the regional stage",
    summary: "The journey starts with regional competition mentoring.",
    paragraphs: [
      "Before the regional competition, the Agal team took part in mentoring. This was the first chapter in a journey toward presenting a price-transparency and harvest-traceability platform for Tawi-Tawi's seaweed supply chain.",
      "These photographs capture the team during that preparation, including an online mentoring session. Behind the app is a team learning, working together, and preparing to share its idea.",
    ],
    status: "Completed",
    photos: [
      {
        id: "mentoring-team", width: 720, height: 960,
        alt: "Three Agal team members pictured on a desktop computer screen during regional competition preparation.",
        caption: "A team moment during the regional mentoring chapter.",
      },
      {
        id: "mentoring-call", width: 720, height: 960,
        alt: "A desktop monitor showing team members and other participants in an online mentoring meeting.",
        caption: "Connecting online for a regional competition mentoring session.",
      },
    ],
  },
  {
    id: "regional-champions",
    number: "02",
    label: "Regional champions",
    title: "A regional win, a shared milestone",
    summary: "Agal became a regional competition champion.",
    paragraphs: [
      "The next chapter brought a milestone worth celebrating: Agal won the regional competition. The championship became part of the team's story as it continued working on the project.",
      "The photographs from this chapter show the people and shared workspace behind the competition effort: laptops around a table, time spent together, and a team carrying the project forward.",
    ],
    status: "Completed",
    photos: [
      {
        id: "regional-team", width: 720, height: 960,
        alt: "A group gathered around a table of laptops at the DICT Tawi-Tawi provincial field office during the regional competition chapter.",
        caption: "Together during the regional competition chapter.",
      },
      {
        id: "regional-collaboration", width: 720, height: 960,
        alt: "An overhead view of the group working around a table with laptops during the regional competition chapter.",
        caption: "The shared workspace behind a regional championship.",
      },
    ],
  },
  {
    id: "trader-interviews",
    number: "03",
    label: "Trader interviews",
    title: "Listening along the trading chain",
    summary: "Taking the project into the places where seaweed is traded.",
    paragraphs: [
      "After the regional competition, the team carried out field interviews with traders. The visits brought Agal's journey into trading spaces, alongside the people and stored harvests that form part of the seaweed supply chain.",
      "Price information and traceability connect several roles. Documenting trader visits is one part of keeping the project grounded in the people it is intended to serve, alongside farmers and buyers.",
    ],
    status: "Completed",
    photos: [
      {
        id: "trader-visit", width: 960, height: 720,
        alt: "Agal team members walking toward wooden trading buildings during a trader field visit.",
        caption: "Arriving at a trading area for the field interviews.",
      },
      {
        id: "trader-conversation", width: 960, height: 720,
        alt: "Team members speaking with people at the counter of a marine products trading business.",
        caption: "A conversation at a marine products trading business.",
      },
      {
        id: "trader-storage", width: 960, height: 720,
        alt: "Stacks of filled white sacks inside a wooden storage building visited during the trader interviews.",
        caption: "A storage area documented during the trader visits.",
      },
      {
        id: "trader-team", width: 960, height: 720,
        alt: "A group photograph taken in a trading area, with filled sacks and wooden buildings behind the group.",
        caption: "A group moment from the trader fieldwork chapter.",
      },
    ],
  },
  {
    id: "farmer-interviews",
    number: "04",
    label: "Farmer interviews",
    title: "Closer to the people behind each harvest",
    summary: "Field interviews with farmers bring the story back to its roots.",
    paragraphs: [
      "The next step was field interviews with farmers. The team visited, asked questions, and took notes in the communities at the beginning of the seaweed supply chain.",
      "The photographs show conversations beside boats and homes, as well as seaweed being dried and examined. They document the setting behind Agal's purpose: making price information and harvest records more useful to the people who grow seaweed.",
    ],
    status: "Completed",
    photos: [
      {
        id: "farmer-conversation", width: 960, height: 720,
        alt: "Agal team members holding interview papers while speaking with people beside a green boat under a tree.",
        caption: "Listening and taking notes during a farmer field interview.",
      },
      storyHeroPhoto,
      {
        id: "farmer-interview", width: 960, height: 720,
        alt: "A team member with a pen and interview papers speaking with a person seated inside a wooden home.",
        caption: "A conversation during the farmer interview chapter.",
      },
      {
        id: "farmer-notes", width: 960, height: 720,
        alt: "A team member holding interview papers during a conversation on a bamboo platform beside wooden homes.",
        caption: "Recording notes during a community visit.",
      },
      {
        id: "seaweed-drying", width: 720, height: 960,
        alt: "A team member crouching beside seaweed spread on a waterfront platform, with boats and hanging seaweed behind.",
        caption: "Documenting seaweed drying during the field visits.",
      },
      {
        id: "seaweed-closeup", width: 720, height: 960,
        alt: "An overhead view of a team member looking at seaweed in a yellow container on a wooden platform.",
        caption: "A closer look at seaweed during the farmer fieldwork.",
      },
    ],
  },
  {
    id: "quezon-city-semifinals",
    number: "05",
    label: "Quezon City semifinals",
    title: "On the road to Quezon City",
    summary: "The journey continues: traveling to compete in the semifinals.",
    paragraphs: [
      "Agal's latest chapter is the ongoing trip to Quezon City to compete in the semifinals. The team carries forward its regional championship and the fieldwork with traders and farmers.",
      "The next stage continues the same purpose: sharing a platform built around price transparency and harvest traceability for Tawi-Tawi's seaweed supply chain.",
    ],
    status: "Ongoing",
    photos: [],
  },
];

export const documentationGuides = [
  {
    href: "/how-it-works",
    label: "The platform",
    title: "Understand how Agal works",
    description: "Follow a harvest record from the phone to the backend and the blockchain ledger.",
  },
  {
    href: "/manual",
    label: "The role-by-role reference",
    title: "Read the user manual",
    description: "Find written instructions for farmers, suppliers and aggregators, and buyers and exporters.",
  },
  {
    href: "/tutorial",
    label: "The visual walkthrough",
    title: "Explore the app tutorial",
    description: "Use annotated app screenshots to explore harvest logging, shipments, and provenance.",
  },
];
