import React, {useRef, useMemo, Suspense} from 'react';
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
  staticFile,
  Easing,
} from 'remotion';
import {Canvas, useFrame, useThree, useLoader} from '@react-three/fiber';
import {RoundedBox} from '@react-three/drei';
import * as THREE from 'three';
import {interFontFamily} from '../design-system/typography';

const fps = 30;

// ════════════════════════════════════════════════════════════════
// Apple-Style Soft Lighting
// ════════════════════════════════════════════════════════════════
function AppleSoftLights() {
  return (
    <>
      {/* Key light — large, soft, from above-right */}
      <directionalLight
        position={[5, 8, 5]}
        intensity={0.6}
        color="#ffffff"
        castShadow
        shadow-mapSize-width={1024}
        shadow-mapSize-height={1024}
      />
      {/* Fill light — from left, softer */}
      <directionalLight
        position={[-4, 4, 2]}
        intensity={0.3}
        color="#f0f4ff"
      />
      {/* Back light — subtle rim */}
      <directionalLight
        position={[0, 3, -5]}
        intensity={0.2}
        color="#e8f0ff"
      />
      {/* Ambient — very soft, no harsh shadows */}
      <ambientLight intensity={0.7} color="#f5f7fa" />
      {/* Hemisphere — sky/ground for natural feel */}
      <hemisphereLight
        args={['#ffffff', '#e8e8e8', 0.4]}
      />
    </>
  );
}

// ════════════════════════════════════════════════════════════════
// Scrolling Screenshot Card — Apple Product Style
// ════════════════════════════════════════════════════════════════
function ScreenshotCard({
  src,
  position: [px, py, pz],
  rotation: [rx, ry, rz] = [0, 0, 0],
  scale = 1,
  frame,
  entryDelay = 0,
}: {
  src: string;
  position: [number, number, number];
  rotation?: [number, number, number];
  scale?: number;
  frame: number;
  entryDelay?: number;
}) {
  const texture = useLoader(THREE.TextureLoader, src);
  const groupRef = useRef<THREE.Group>(null);

  // Auto-size plane
  const maxW = 3.32;
  const maxH = 2.12;
  const imgW = texture.image?.width || 1280;
  const imgH = texture.image?.height || 800;
  const imgAspect = imgW / imgH;
  const cardAspect = maxW / maxH;

  let planeW: number, planeH: number;
  if (imgAspect > cardAspect) {
    planeW = maxW * 0.95;
    planeH = planeW / imgAspect;
  } else {
    planeH = maxH * 0.95;
    planeW = planeH * imgAspect;
  }
  planeW = Math.max(0.5, Math.min(planeW, maxW));
  planeH = Math.max(0.5, Math.min(planeH, maxH));

  // Entry animation
  const entryProgress = interpolate(
    frame,
    [entryDelay, entryDelay + 20],
    [0, 1],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'},
  );
  const easedEntry = Easing.out(Easing.cubic)(entryProgress);
  const startY = py + 5;
  const currentY = interpolate(easedEntry, [0, 1], [startY, py]);
  const currentScale = interpolate(easedEntry, [0, 1], [0.3, scale]);

  // Gentle drift
  const driftRotY = ry + interpolate(frame, [0, 450], [-0.08, 0.08]);
  const tiltX = Math.sin(frame * 0.01) * 0.03;

  // Short scroll
  useFrame(() => {
    if (!texture) return;
    const t = (frame % 450) / 450;
    const scrollAmount = (Math.sin(t * Math.PI * 2) + 1) / 2;
    texture.offset.y = scrollAmount * 0.08;
    texture.wrapS = THREE.ClampToEdgeWrapping;
    texture.wrapT = THREE.ClampToEdgeWrapping;
    texture.needsUpdate = true;
  });

  return (
    <group
      ref={groupRef}
      position={[px, currentY, pz]}
      rotation={[rx + tiltX, driftRotY, rz]}
      scale={currentScale}
    >
      {/* Device frame — Apple silver */}
      <RoundedBox args={[3.4, 2.2, 0.12]} radius={0.08} smoothness={6}>
        <meshStandardMaterial
          color="#d1d5db"
          metalness={0.6}
          roughness={0.15}
        />
      </RoundedBox>

      {/* Inner bezel */}
      <RoundedBox args={[3.32, 2.12, 0.125]} radius={0.07} smoothness={6}>
        <meshStandardMaterial
          color="#000000"
          metalness={0.1}
          roughness={0.4}
        />
      </RoundedBox>

      {/* Screen */}
      <mesh position={[0, 0, 0.065]}>
        <planeGeometry args={[planeW, planeH]} />
        <meshBasicMaterial
          map={texture}
          toneMapped={false}
        />
      </mesh>

      {/* Soft shadow */}
      <mesh position={[0, -1.4, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[3.6, 2.4]} />
        <meshBasicMaterial
          color="#000000"
          transparent
          opacity={0.15}
        />
      </mesh>
    </group>
  );
}

// ════════════════════════════════════════════════════════════════
// Soft Camera — Gentle, Apple-style
// ════════════════════════════════════════════════════════════════
function SoftCamera() {
  const frame = useCurrentFrame();
  const {camera} = useThree();
  const progress = frame / 450;
  const angle = interpolate(progress, [0, 1], [0.15, 0.4]);
  const radius = interpolate(progress, [0, 0.4, 1], [5.5, 4.8, 4.3]);
  const height = interpolate(progress, [0, 1], [0.6, 0.4]);
  const x = Math.sin(angle) * radius;
  const z = Math.cos(angle) * radius;
  camera.position.set(x, height, z);
  camera.lookAt(0, 0, 0);
  return null;
}

// ════════════════════════════════════════════════════════════════
// Minimal Dust
// ════════════════════════════════════════════════════════════════
function Dust() {
  const count = 10;
  const mesh = useRef<THREE.InstancedMesh>(null);
  const dummy = useMemo(() => new THREE.Object3D(), []);
  const particles = useMemo(() => {
    return Array.from({length: count}).map(() => ({
      x: (Math.random() - 0.5) * 8,
      y: (Math.random() - 0.5) * 4,
      z: (Math.random() - 0.5) * 3,
      speed: 0.05 + Math.random() * 0.1,
      phase: Math.random() * Math.PI * 2,
    }));
  }, []);

  useFrame(({clock}) => {
    if (!mesh.current) return;
    particles.forEach((p, i) => {
      dummy.position.set(
        p.x,
        p.y + Math.sin(clock.elapsedTime * p.speed + p.phase) * 0.05,
        p.z
      );
      dummy.updateMatrix();
      mesh.current!.setMatrixAt(i, dummy.matrix);
    });
    mesh.current.instanceMatrix.needsUpdate = true;
  });

  return (
    <instancedMesh ref={mesh} args={[undefined, undefined, count]}>
      <circleGeometry args={[0.008, 6]} />
      <meshBasicMaterial color="#aab4c4" transparent opacity={0.1} />
    </instancedMesh>
  );
}

// ════════════════════════════════════════════════════════════════
// Apple-Style Scene — Light, clean, minimal
// ════════════════════════════════════════════════════════════════
function Scene({imageUrl, frame}: {imageUrl: string; frame: number}) {
  return (
    <>
      <SoftCamera />
      <AppleSoftLights />

      {/* Light gradient background */}
      <mesh>
        <sphereGeometry args={[20, 16, 16]} />
        <meshBasicMaterial color="#f0f2f5" side={THREE.BackSide} />
      </mesh>

      <fog attach="fog" args={['#f0f2f5', 10, 20]} />

      <ScreenshotCard
        src={imageUrl}
        position={[0, 0, 0]}
        rotation={[0.02, 0.12, 0]}
        scale={1.3}
        frame={frame}
        entryDelay={5}
      />

      <ScreenshotCard
        src={imageUrl}
        position={[-2.5, -0.6, -2]}
        rotation={[0.04, -0.3, -0.02]}
        scale={0.65}
        frame={frame}
        entryDelay={15}
      />

      <ScreenshotCard
        src={imageUrl}
        position={[2.5, 0.3, -1.5]}
        rotation={[-0.01, 0.25, 0.02]}
        scale={0.55}
        frame={frame}
        entryDelay={20}
      />

      <Dust />
    </>
  );
}

// ════════════════════════════════════════════════════════════════
// 2D Text — Apple Typography
// ════════════════════════════════════════════════════════════════
function TextOverlay({kicker, title, cta, frame}: {
  kicker: string;
  title: string;
  cta: string;
  frame: number;
}) {
  const kickerSpring = spring({frame: frame - 8, fps, config: {damping: 14, stiffness: 180}});
  const titleSpring = spring({frame: frame - 15, fps, config: {damping: 12, stiffness: 160, mass: 1.1}});
  const kickerScale = interpolate(kickerSpring, [0, 1], [0.8, 1.05]);
  const kickerSettle = interpolate(frame, [15, 22], [kickerScale, 1]);
  const titleScale = interpolate(titleSpring, [0, 1], [0.7, 1.08]);
  const titleSettle = interpolate(frame, [22, 32], [titleScale, 1]);
  const kickerOp = interpolate(frame, [8, 18], [0, 1], {extrapolateLeft: 'clamp'});
  const titleOp = interpolate(frame, [15, 28], [0, 1], {extrapolateLeft: 'clamp'});

  const relFrame = frame - 100;
  const pulse = Math.sin(relFrame * 0.08) * 0.5 + 0.5;
  const pulseScale = 1 + pulse * 0.03;
  const glowOpacity = 0.3 + pulse * 0.4;
  const ctaOp = interpolate(frame, [100, 115], [0, 1], {extrapolateLeft: 'clamp'});
  const ctaSpring = spring({frame: relFrame, fps, config: {damping: 10, stiffness: 200}});

  return (
    <AbsoluteFill
      style={{
        pointerEvents: 'none',
        zIndex: 10,
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        padding: '70px 48px',
      }}
    >
      <div style={{display: 'flex', flexDirection: 'column', gap: 14}}>
        <div style={{transform: `scale(${kickerSettle}) translateY(${(1 - kickerSpring) * 10}px)`, opacity: kickerOp}}>
          <div style={{fontFamily: interFontFamily, fontSize: 14, fontWeight: 600, letterSpacing: '0.25em', textTransform: 'uppercase', color: '#666666'}}>
            {kicker}
          </div>
        </div>
        <div style={{transform: `scale(${titleSettle}) translateY(${(1 - titleSpring) * 25}px)`, opacity: titleOp}}>
          <div style={{fontFamily: interFontFamily, fontSize: 44, fontWeight: 800, lineHeight: 1.15, color: '#111111', letterSpacing: '-0.02em', maxWidth: '90%'}}>
            {title}
          </div>
        </div>
      </div>

      <div style={{display: 'flex', justifyContent: 'center', transform: `scale(${ctaSpring * pulseScale})`, opacity: ctaOp}}>
        <div style={{background: 'linear-gradient(135deg, #0071E3 0%, #5E5CE6 100%)', color: '#FFFFFF', padding: '16px 44px', borderRadius: 100, fontFamily: interFontFamily, fontSize: 20, fontWeight: 700, boxShadow: `0 0 ${20 + pulse * 30}px rgba(0,113,227,${glowOpacity}), 0 8px 24px rgba(0,0,0,0.15)`}}>
          {cta}
        </div>
      </div>
    </AbsoluteFill>
  );
}

// ════════════════════════════════════════════════════════════════
// MAIN VIDEO — Apple Style
// ════════════════════════════════════════════════════════════════
export type Promo3DVideoProps = {
  kicker: string;
  title: string;
  benefit: string;
  cta: string;
  imageUrl?: string;
  durationInSeconds?: number;
  logoText?: string;
};

export const Promo3DVideo: React.FC<Promo3DVideoProps> = ({
  kicker, title, benefit, cta, imageUrl, durationInSeconds = 15, logoText,
}) => {
  const {width, height} = useVideoConfig();
  const frame = useCurrentFrame();
  const resolvedImage = imageUrl ? (imageUrl.startsWith('http') ? imageUrl : staticFile(imageUrl)) : undefined;

  return (
    <AbsoluteFill style={{background: '#f0f2f5', width, height}}>
      <div style={{position: 'absolute', top: 0, left: 0, width: '100%', height: '100%'}}>
        <Suspense fallback={
          <AbsoluteFill style={{background: '#f0f2f5', display: 'flex', justifyContent: 'center', alignItems: 'center'}}>
            <div style={{fontFamily: interFontFamily, fontSize: 18, color: '#888888'}}>Loading...</div>
          </AbsoluteFill>
        }>
          <Canvas
            camera={{position: [0, 0.6, 5.5], fov: 40}}
            style={{width: '100%', height: '100%'}}
            gl={{antialias: true, alpha: false, powerPreference: 'high-performance'}}
          >
            {resolvedImage && <Scene imageUrl={resolvedImage} frame={frame} />}
          </Canvas>
        </Suspense>
      </div>

      <TextOverlay kicker={kicker} title={title} cta={cta} frame={frame} />

      <div style={{position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', background: 'radial-gradient(ellipse at center, transparent 60%, rgba(240,242,245,0.6) 100%)', pointerEvents: 'none', zIndex: 5}} />
    </AbsoluteFill>
  );
};

export const defaultPromo3DProps: Promo3DVideoProps = {
  kicker: 'Product Update',
  title: 'AI Follow-Ups, Now in Real Time',
  benefit: 'Never lose high-intent leads between inquiry and call.',
  cta: 'Turn it on today.',
  imageUrl: undefined,
  durationInSeconds: 15,
  logoText: 'LUSTRE',
};

export const promo3DDurationInFrames = 450;
