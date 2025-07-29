{ pkgs }: {
  deps = [
    pkgs.nodejs-18_x
    pkgs.nodePackages.typescript
    pkgs.nodePackages.npm
    pkgs.python39
    pkgs.python39Packages.pip
    pkgs.postgresql_15
    pkgs.redis
    pkgs.git
    pkgs.curl
    pkgs.wget
    pkgs.jq
    pkgs.docker
    pkgs.docker-compose
  ];
} 