// Mock data for Henné Artisanal website

export const mockData = {
  navigation: [
    { label: 'Accueil', href: '/', active: true },
    { label: 'Galerie', href: '/galerie' },
    { label: 'Tarifs', href: '/tarifs' },
    { label: 'Avis', href: '/avis' },

    { label: 'Mon Espace', href: '/mon-espace', icon: 'user' },
    { label: 'Déconnexion', href: '/deconnexion', icon: 'log-out' }
  ],

  hero: {
    title: "L'Art du Henné",
    subtitle: "Sublimé",
    description: "Découvrez la beauté des motifs traditionnels avec nos créations uniques réalisées au henné 100% naturel",
    primaryButton: "Réserver une Séance",
    secondaryButton: "En Savoir Plus",
    backgroundImage: "https://images.unsplash.com/photo-1629332791128-58f00882964d?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1ODB8MHwxfHNlYXJjaHwxfHxoZW5uYSUyMGhhbmRzfGVufDB8fHx8MTc1NzA3MTE2MXww&ixlib=rb-4.1.0&q=85"
  },

  features: {
    title: "Pourquoi Choisir Notre Service ?",
    subtitle: "Une expérience unique alliant tradition, qualité et créativité pour sublimer votre beauté naturelle",
    items: [
      {
        icon: "map-pin",
        title: "Art Traditionnel",
        description: "Designs authentiques inspirés des traditions ancestrales"
      },
      {
        icon: "user",
        title: "Expérience Personnalisée",
        description: "Chaque création est unique et adaptée à vos goûts"
      },
      {
        icon: "star",
        title: "Qualité Premium",
        description: "Henné 100% naturel pour des résultats durables"
      },
      {
        icon: "clock",
        title: "Service Rapide",
        description: "Réservation flexible selon votre disponibilité"
      }
    ]
  },

  cta: {
    title: "Prête à Rayonner ?",
    description: "Réservez dès maintenant votre séance de henné et laissez-vous enchanter par l'art ancestral de la beauté naturelle",
    buttonText: "Prendre Rendez-vous"
  },

  pricing: {
    title: "Nos Tarifs",
    subtitle: "Des prestations adaptées à tous vos besoins, de la création simple aux événements exceptionnels",
    plans: [
      {
        icon: "heart",
        name: "Très simple",
        price: "5€",
        duration: "Durée: 10-15 min",
        description: "Design sur un doigt",
        features: [
          "Design simple sur un doigt"
        ],
        buttonText: "Réserver",
        popular: false
      },
      {
        icon: "heart",
        name: "Simple",
        price: "8€",
        duration: "Durée: 20-30 min",
        description: "Designs simples et élégants pour toute occasion",
        features: [
          "Design simple sur une main"
        ],
        buttonText: "Réserver",
        popular: true
      },
      {
        icon: "star",
        name: "Chargé",
        price: "12€",
        duration: "Durée: 45min - 1h",
        description: "Créations détaillées et ornementées",
        features: [
          "Design sur les deux mains",
          "Motifs complexes",
          "Photos incluses"
        ],
        buttonText: "Réserver",
        popular: false
      },
      {
        icon: "crown",
        name: "Mariée",
        price: "20€",
        duration: "Durée: 1h - 1h30",
        description: "Service spécial mariée avec motifs exceptionnels",
        features: [
          "Mains et avant-bras",
          "Designs personnalisés",
          "Service privilégié",
          "Séance photo incluse"
        ],
        buttonText: "Réserver",
        popular: false
      }
    ]
  },

  testimonials: {
    title: "Avis Clients",
    subtitle: "Découvrez les témoignages de nos clients qui ont vécu une expérience unique avec nos créations au henné",
    rating: {
      score: "5",
      text: "Basé sur 47 avis vérifiés"
    },
    reviews: [
      {
        id: 1,
        name: "Sarah M.",
        timeAgo: "Il y a 2 semaines",
        rating: 5,
        avatar: "SM",
        review: "Une expérience absolument magique ! Les motifs étaient d'une finesse incroyable et ont duré plus de 2 semaines. Je recommande vivement pour un mariage ou toute occasion spéciale.",
        service: "Henné Mariée"
      },
      {
        id: 2,
        name: "Amina K.",
        timeAgo: "Il y a 1 mois",
        rating: 5,
        avatar: "AK",
        review: "Service impeccable et design magnifique. L'artiste a su parfaitement comprendre mes attentes et créer un motif unique. La qualité du henné est exceptionnelle.",
        service: "Henné Traditionnel"
      },
      {
        id: 3,
        name: "Léa D.",
        timeAgo: "Il y a 3 semaines",
        rating: 5,
        avatar: "LD",
        review: "Premier essai du henné et je suis conquise ! Accueil chaleureux, conseils précieux et résultat au-delà de mes espérances. J'y retournerai sans hésiter.",
        service: "Henné Simple"
      },
      {
        id: 4,
        name: "Fatima B.",
        timeAgo: "Il y a 1 semaine",
        rating: 5,
        avatar: "FB",
        review: "Pour mon mariage, j'ai fait appel à leurs services et c'était parfait. Les motifs traditionnels étaient respectés à la perfection. Toutes mes invitées étaient émerveillées.",
        service: "Henné Mariée"
      },
      {
        id: 5,
        name: "Claire L.",
        timeAgo: "Il y a 2 mois",
        rating: 5,
        avatar: "CL",
        review: "Excellente prestation ! Le henné est de très bonne qualité, les motifs sont fins et détaillés. L'ambiance est relaxante et l'artiste très professionnelle.",
        service: "Henné Traditionnel"
      },
      {
        id: 6,
        name: "Nadia R.",
        timeAgo: "Il y a 3 semaines",
        rating: 5,
        avatar: "NR",
        review: "Service à domicile parfait pour notre événement familial. Tout le monde était ravi ! Les enfants comme les adultes ont adoré leurs motifs personnalisés.",
        service: "Atelier Groupe"
      }
    ],
    stats: [
      {
        number: "100%",
        label: "Satisfaction"
      },
      {
        number: "200+",
        label: "Clientes"
      },
      {
        number: "3 ans",
        label: "Expérience"
      }
    ]
  },

  contact: {
    title: "Réservation",
    subtitle: "Réservez votre séance de henné en quelques clics. Nous vous contacterons pour confirmer tous les détails.",
    form: {
      fields: [
        { name: 'fullName', label: 'Nom complet', type: 'text', required: true, placeholder: 'Votre nom' },
        { name: 'email', label: 'Email', type: 'email', required: true, placeholder: 'votre@email.com' },
        { name: 'phone', label: 'Téléphone', type: 'tel', required: true, placeholder: '06 12 34 56 78' },
        { name: 'service', label: 'Service souhaité', type: 'select', required: true, options: [
          'Choisissez votre service',
          'Simple - 8€',
          'Chargé - 12€',
          'Mariée - 20€',
          'Autre demande'
        ]},
        { name: 'date', label: 'Date souhaitée', type: 'date', required: true },
        { name: 'time', label: 'Heure préférée', type: 'select', required: true, options: [
          'Choisir un horaire',
          '9h00',
          '10h00',
          '11h00',
          '14h00',
          '15h00',
          '16h00',
          '17h00'
        ]},
        { name: 'location', label: 'Lieu souhaité', type: 'select', required: false, options: [
          'Choisir le lieu',
          'En salon',
          'À domicile',
          'Événement'
        ]},
        { name: 'message', label: 'Message (optionnel)', type: 'textarea', required: false, placeholder: 'Décrivez vos souhaits particuliers, motifs préférés...' }
      ],
      submitText: 'Envoyer ma Demande de Réservation'
    },
    info: {
      title: "Contact Direct",
      phone: "06 12 34 56 78",
      email: "contact@hennalash.fr",
      address: {
        street: "123 Rue de la Beauté",
        city: "75001 Paris"
      },
      hours: {
        title: "Horaires d'Ouverture",
        schedule: [
          { days: "Lundi - Vendredi", hours: "9h - 18h" },
          { days: "Samedi", hours: "9h - 17h" },
          { days: "Dimanche", hours: "Sur RDV" }
        ]
      },
      notes: {
        title: "À Savoir",
        items: [
          "Confirmation par SMS dans les 24h",
          "Possibilité d'annulation jusqu'à 24h avant",
          "Paiement en espèces ou par carte",
          "Henné 100% naturel et végétal",
          "Durée: 1 à 3 semaines selon la peau"
        ]
      }
    }
  }
};